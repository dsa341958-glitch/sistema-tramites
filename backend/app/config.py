import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
TOKEN_HORAS = int(os.getenv("TOKEN_HORAS", "8"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")