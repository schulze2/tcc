import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', "uma_chave_secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        str(BASE_DIR / 'uploads' / 'documentos')
    )


class DevelopmentConfig(Config):
    DEBUG = True
