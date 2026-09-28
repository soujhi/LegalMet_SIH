import os
import shutil
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR.parent / "data"

# Handle serverless/ephemeral environments (like Vercel / AWS Lambda)
IS_SERVERLESS = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")

if IS_SERVERLESS:
    STORAGE_ROOT = Path("/tmp") / "storage"
    DEFAULT_DB = Path("/tmp") / "legalmet.db"
    bundled_db = BASE_DIR.parent / "database" / "legalmet.db"
    if not DEFAULT_DB.exists() and bundled_db.exists():
        try:
            shutil.copyfile(bundled_db, DEFAULT_DB)
        except Exception:
            pass
else:
    STORAGE_ROOT = BASE_DIR / "storage"
    candidate_dbs = [
        BASE_DIR.parent / "database" / "legalmet.db",
        BASE_DIR / "database" / "legalmet.db",
        Path("database/legalmet.db"),
        Path("../database/legalmet.db")
    ]
    DEFAULT_DB = next((p for p in candidate_dbs if p.exists()), candidate_dbs[0])

UPLOADS_DIR = STORAGE_ROOT / "uploads"
CERTIFICATES_DIR = STORAGE_ROOT / "certificates"
QR_DIR = STORAGE_ROOT / "qr_codes"
DOCA_PDFS_DIR = DATA_DIR / "government" / "doca_model_approval" / "pdfs"

try:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

class Settings(BaseModel):
    PROJECT_NAME: str = "LegalMet Verify API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "legalmet-super-secret-production-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Defaults to SQLite in workspace root database folder
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{DEFAULT_DB}"
    )
    
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

settings = Settings()
