import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data"
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
CERTIFICATES_DIR = BASE_DIR / "storage" / "certificates"
QR_DIR = BASE_DIR / "storage" / "qr_codes"
DOCA_PDFS_DIR = DATA_DIR / "government" / "doca_model_approval" / "pdfs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
QR_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "LegalMet Verify API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "legalmet-super-secret-production-key-sih26036-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Defaults to SQLite in workspace root database folder
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR.parent / 'database' / 'legalmet.db'}"
    )
    
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

settings = Settings()
