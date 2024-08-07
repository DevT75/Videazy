import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    DB_USER: str = os.getenv('MYSQL_USER')
    DB_PASSWORD: str = os.getenv('MYSQL_PASSWORD')
    DB_NAME: str = os.getenv('MYSQL_DB')
    DB_HOST: str = os.getenv('MYSQL_SERVER')
    DB_PORT: str = os.getenv('MYSQL_PORT')
    DATABASE_URL: str = os.getenv('MYSQL_URI') or f"mysql+pymysql://{DB_USER}:%s@{DB_HOST}:{DB_PORT}/{DB_NAME}"% quote_plus(DB_PASSWORD)
    JWT_SECRET:str = os.getenv('JWT_SECRET','8e6f560a9fc1ffbf82e2e1e5ecc4fccd7cfa4a5d503a11b5802c080512aaf8b8')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM','HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('JWT_TOKEN_EXPIRE_MINUTES',60)

def get_settings()->Settings:
    return Settings()