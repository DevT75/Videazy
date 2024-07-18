from fastapi import APIRouter,status,Depends,Request,UploadFile,File
from typing import List
from fastapi.responses import FileResponse
from core.db import get_db
from fastapi.exceptions import HTTPException
from users.models import UserModel
from video.model import MediaModel
from core.security import get_current_user, oauth2_scheme
from sqlalchemy.orm import Session
from typing import Annotated,Union
from pathlib import Path
import cloudinary
import cloudinary.uploader
import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime
from starlette.requests import Request
import shutil
import ffmpeg
import sys

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_NAME'),
    api_key = os.getenv('CLOUDINARY_KEY'),
    api_secret = os.getenv('CLOUDINARY_SECRET'),
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
    # dependencies=[Depends(oauth2_scheme)]
)

global_file_size = 0

async def check_files_size(request: Request, files: List[UploadFile]):
    max_size = 1024 * 1024 * 1024  # Maximum size: 10 MB
    if request.user:
        max_size *= 2  # Double the size limit for authenticated users
    total_size = 0
    for file in files:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        total_size += file_size
        # global_file_size = file_size
        file.file.seek(0)  # Reset file pointer
    if total_size > max_size:
        raise HTTPException(status_code=413, detail="Total file size exceeds the limit")
    return files

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv','webm'}

codec_options = {
    'vp8_vorbis': {
        'c:v': 'libvpx',
        'b:v': '1M',
        'c:a': 'libvorbis'
    },
    'vp9_opus': {
        'c:v': 'libvpx-vp9',
        'b:v': '1M',
        'c:a': 'libopus'
    },
    'h264_aac': {
        'c:v': 'libx264',
        'b:v': '1M',
        'c:a': 'aac'
    },
    'h265_opus': {
        'c:v': 'libx265',
        'b:v': '1M',
        'c:a': 'libopus'
    }
}

def get_codec_options(codec_name):
    # Map codec names to codec options and presets
    if codec_name == 'h264':
        options = codec_options['h264_aac']
        preset = '-preset fast'  # Example preset for H.264
    elif codec_name == 'vp9':
        options = codec_options['vp9_opus']
        preset = '-preset ultrafast'  # Example preset for VP9
    elif codec_name == 'vp8':
        options = codec_options['vp8_vorbis']
        preset = '-preset veryfast'  # Example preset for VP8
    else:
        # Default to VP8/Vorbis for unknown codecs
        options = codec_options['vp8_vorbis']
        preset = '-preset veryfast'  # Example preset for unknown codecs
    return options, preset

upload_folder = 'static/uploads'
compressed_folder = 'static/compressed'

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)


@router.post("/",status_code=status.HTTP_200_OK)
async def upload_media_unauthenticated(req:Request,files: List[UploadFile]):
    results = []
    for file in files:
        if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail="Invalid file type")
        result = await compress_video(file=file)
        results.append(result)
    return results

@router.post("/me",status_code=status.HTTP_200_OK)
async def upload_media_authenticated(req:Request,current_user:Annotated[UserModel,Depends(get_current_user)],files:List[UploadFile] = Depends(check_files_size),db:Session = Depends(get_db)):
    results = []
    for file in files:
        if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail="Invalid file type")
        compressed_video = await compress_video(file=file)
        compressed_file_path = os.path.join(compressed_folder,compressed_video["filename"])
        upload_response = cloudinary.uploader.upload(compressed_file_path, resource_type="auto",public_id=f"compressed_{file.filename}{req.user.id}")
        cloudinary_video_url = upload_response['secure_url']
        # Save video metadata in the database
        compressed_video= MediaModel(
                user_id = req.user.id,
                type=file.headers["content-type"].split('/')[0],
                url=cloudinary_video_url,
                uploaded_at=datetime.now()
        )
        db.add(compressed_video)
        db.commit()
        db.refresh(compressed_video)
        results.append({
            "filename": file.filename,
            "download_url": f"/download/{f'compressed_{file.filename}'}"
        })

    return { "download_url" : f"/download/{f'compressed_{file.filename}'}" }



async def compress_video(file: UploadFile):
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(compressed_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    compressed_filename = 'compressed_' + file.filename
    compressed_file_path = os.path.join(compressed_folder, compressed_filename)
    
    if os.path.exists(compressed_file_path):
        print("Returning already compressed file")
        return {"filename": compressed_filename, "url": f"/download/{compressed_filename}", "status": "already_compressed"}
    else:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


    ffmpeg_command = [ 'ffmpeg', '-i', file_path ]
    file_codec = ffmpeg.probe(file_path)["streams"][0]["codec_name"]
    options,preset = get_codec_options(file_codec)
    for key, value in options.items():
        ffmpeg_command.extend(['-{}'.format(key), value])
    file_duration = get_length(file_path)
    print(file_duration)
    ffmpeg_command.extend(['-crf','24'])
    # preset options
    ffmpeg_command.extend(preset.split())
    ffmpeg_command.append(compressed_file_path)

    try:
        subprocess.run(ffmpeg_command, check=True)
        return {"filename": f"compressed_{file.filename}", "url": f"/download/{f'compressed_{file.filename}'}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while compressing video: {e}")