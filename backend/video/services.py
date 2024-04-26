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