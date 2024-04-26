from fastapi import APIRouter,status,Depends,Request,UploadFile,File,Request
from core.db import get_db
from fastapi.exceptions import HTTPException
from video.model import MediaModel
from core.security import oauth2_scheme
from sqlalchemy.orm import Session
from pathlib import Path
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from datetime import datetime

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
    dependencies=[Depends(oauth2_scheme)]
)


@router.post("/",status_code=status.HTTP_200_OK)
async def upload_media(req:Request,file: UploadFile = File(...),db: Session = Depends(get_db)):
    if not req.user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    media_uri = cloudinary.uploader.upload(file.file, resource_type="auto",public_id=f"{file.filename}{req.user.id}")
    new_media = MediaModel(
        user_id=req.user.id,
        type=file.headers["content-type"].split('/')[0],
        url=media_uri["secure_url"],
        uploaded_at=datetime.now()
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return {"message":"File Uploaded Succesfully!!"}