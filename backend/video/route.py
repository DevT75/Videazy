import asyncio
from fastapi import APIRouter, status, Depends, Request, UploadFile, File
from typing import List
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from core.db import get_db
from fastapi.exceptions import HTTPException
from users.models import UserModel
from video.model import MediaModel
from core.security import get_current_user, oauth2_scheme
from sqlalchemy.orm import Session
from typing import Annotated, Union
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
)

global_file_size = 0
progress_tracker = {}


async def check_files_size(request: Request, files: List[UploadFile]):
    max_size = 1024 * 1024 * 1024  # Maximum size: 10 MB
    if request.user:
        max_size *= 2  # Double the size limit for authenticated users
    total_size = 0
    for file in files:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        total_size += file_size
        file.file.seek(0)  # Reset file pointer
    if total_size > max_size:
        raise HTTPException(status_code=413, detail="Total file size exceeds the limit")
    return files

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

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
    if codec_name == 'h264':
        options = codec_options['h264_aac']
        preset = '-preset fast'
    elif codec_name == 'vp9':
        options = codec_options['vp9_opus']
        preset = '-preset ultrafast'
    elif codec_name == 'vp8':
        options = codec_options['vp8_vorbis']
        preset = '-preset veryfast'
    else:
        options = codec_options['vp8_vorbis']
        preset = '-preset veryfast'
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

@router.get("/")
async def upload():
    return {"message": "You may upload media here!!"}

@router.post("/", status_code=status.HTTP_200_OK)
async def upload_media_unauthenticated(req: Request, files: List[UploadFile]):
    results = []
    for file in files:
        if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail="Invalid file type")
        task_id = f"{file.filename}"
        # data = await compress_video(file=file, task_id=task_id)
        asyncio.create_task(compress_video(file=file, task_id=task_id))
        results.append({
            "filename": file.filename,
            "download_url": f"/download/{file.filename}",
            "progress_url": f"/upload/progress/{task_id}"
        })
    return JSONResponse(content=results)

@router.post("/me", status_code=status.HTTP_200_OK)
async def upload_media_authenticated(req: Request, current_user: Annotated[UserModel, Depends(get_current_user)], files: List[UploadFile] = Depends(check_files_size), db: Session = Depends(get_db)):
    results = []
    for file in files:
        if not file.filename.endswith(tuple(ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail="Invalid file type")

        task_id = f"{file.filename}"

        asyncio.create_task(compress_video(file=file, task_id=task_id, isAuthenticated=True, user_id=current_user.id, db=db))

        # compressed_video = await compress_video(file=file, task_id=task_id)
        # compressed_file_path = os.path.join(compressed_folder, compressed_video["filename"])
        # upload_response = cloudinary.uploader.upload(compressed_file_path, resource_type="auto", public_id=f"compressed_{file.filename}{req.user.id}")
        # cloudinary_video_url = upload_response['secure_url']
        # compressed_video = MediaModel(
        #         user_id = req.user.id,
        #         type=file.headers["content-type"].split('/')[0],
        #         url=cloudinary_video_url,
        #         uploaded_at=datetime.now()
        # )
        # db.add(compressed_video)
        # db.commit()
        # db.refresh(compressed_video)
        results.append({
            "filename": file.filename,
            "download_url": f"/download/{file.filename}",
            "progress_url": f"/upload/progress/{task_id}"
        })
    return JSONResponse(content=results)

@router.get("/progress/{task_id}", response_class=StreamingResponse)
async def get_progress(task_id: str):
    print(task_id)
    async def event_generator():
        while task_id in progress_tracker:
            progress = progress_tracker[task_id]
            yield f"data: {progress}\n\n"
            await asyncio.sleep(0.5)  # Update every 0.5 seconds

        yield "data: 100\n\n"  # Send 100% progress when the task is done

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Get the total number of frames in the input video
# def get_total_frames(file_path):
#     # Run ffmpeg command to fetch frame count information
#     ffmpeg_command = ['ffmpeg', '-i', file_path]
#     process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

#     frame_count = None
#     for line in process.stderr:
#         if "frame=" in line:
#             frame_count = int(line.split("frame=")[1].strip().split()[0])
#             break

#     return frame_count

def get_total_frames(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return int(result.stdout.strip())


async def compress_video(file: UploadFile, task_id: str, isAuthenticated: bool = False, user_id: int = None, db: Session = None):
    print(task_id)
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

    ffmpeg_command = ['ffmpeg', '-i', file_path]
    file_codec = ffmpeg.probe(file_path)["streams"][0]["codec_name"]
    options, preset = get_codec_options(file_codec)
    for key, value in options.items():
        ffmpeg_command.extend(['-{}'.format(key), value])
    file_duration = get_length(file_path)
    print(file_duration)
    ffmpeg_command.extend(['-crf', '24'])
    ffmpeg_command.extend(preset.split())
    ffmpeg_command.append(compressed_file_path)

    # try:
    #     subprocess.run(ffmpeg_command, check=True)
    #     return {"filename": f"compressed_{file.filename}", "url": f"/download/{f'compressed_{file.filename}'}"}
    # except subprocess.CalledProcessError as e:
    #     raise HTTPException(status_code=500, detail=f"Error occurred while compressing video: {e}")

    # try:
    #     process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    #     progress_tracker[task_id] = 0
    #     # print(process.stdout)
    #     for line in process.stderr:
    #         print(line)
    #         if 'out_time' in line:  # FFmpeg outputs the current time in the compression
    #             # Parse progress (out_time)
    #             time_str = line.split('=')[1]
    #             current_time = float(time_str)
    #             file_duration = get_length(file_path)
    #             progress = (current_time / file_duration) * 100
    #             progress_tracker[task_id] = round(progress, 2)  # Update progress
    #             print(progress_tracker[task_id])

    #     process.communicate()  # Wait for the process to finish

    #     # Compression complete, remove the progress tracker
    #     del progress_tracker[task_id]

    #     return {"filename": f"compressed_{file.filename}", "url": f"/download/{f'compressed_{file.filename}'}"}

    # except subprocess.CalledProcessError as e:
    #     raise HTTPException(status_code=500, detail=f"Error occurred while compressing video: {e}")

    try:
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        progress_tracker[task_id] = 0

        # Track progress based on frames
        total_frames = get_total_frames(file_path)
        # print(f"Total frames: {total_frames}")
        for line in process.stderr:
            # print(f"FFmpeg stderr: {line}")  # Print stderr for debugging

            # Check if the line contains 'frame=' or 'frames=' for frame progress
            if 'frame=' in line:
                current_frame = int(line.split('frame=')[1].strip().split()[0])
                # print(f"Current frame: {current_frame}")
                progress = (current_frame / total_frames) * 100 if total_frames else 0
                progress_tracker[task_id] = round(progress, 2)
                print(f"Progress: {progress_tracker[task_id]}%")

        process.communicate()
        del progress_tracker[task_id]  # Remove progress entry after completion
        if(isAuthenticated):
            upload_response = cloudinary.uploader.upload(compressed_file_path, resource_type="auto", public_id=f"compressed_{file.filename}{user_id}")
            cloudinary_video_url = upload_response['secure_url']
            compressed_video = MediaModel(
                    user_id = user_id,
                    type=file.headers["content-type"].split('/')[0],
                    url=cloudinary_video_url,
                    uploaded_at=datetime.now()
            )
            db.add(compressed_video)
            db.commit()
            db.refresh(compressed_video)
        return {"filename": f"compressed_{file.filename}", "url": f"/download/{f'compressed_{file.filename}'}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while compressing video: {e}")