import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde el directorio de backend
base_dir = Path(__file__).resolve().parent
dotenv_path = base_dir / ".env"
load_dotenv(dotenv_path)


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1003418409")
    DB_NAME = os.getenv("DB_NAME", "huellitas_felices")
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))
    JWT_SECRET = os.getenv("JWT_SECRET", "huellitas_felices_secret_key_2026")
    JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", 8))
    API_KEY = os.getenv("API_KEY", "huellitas_api_secret_key_2026")
