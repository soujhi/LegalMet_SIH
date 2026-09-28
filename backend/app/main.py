from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings, CERTIFICATES_DIR, QR_DIR, UPLOADS_DIR, DOCA_PDFS_DIR
from app.db_init import init_db

from app.routers import (
    auth, instruments, applications, schedule, verification,
    rules, certificates, public_verify, ocr, analytics, audit
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Online Verification System for Weighing and Measuring Instruments API"
)

# Enable CORS for local development and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts for downloaded PDFs, QR codes, and uploads
app.mount("/storage/certificates", StaticFiles(directory=str(CERTIFICATES_DIR)), name="certificates")
app.mount("/storage/qr_codes", StaticFiles(directory=str(QR_DIR)), name="qr_codes")
app.mount("/storage/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
if DOCA_PDFS_DIR.exists():
    app.mount("/storage/doca_pdfs", StaticFiles(directory=str(DOCA_PDFS_DIR)), name="doca_pdfs")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(instruments.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(schedule.router, prefix=settings.API_V1_STR)
app.include_router(verification.router, prefix=settings.API_V1_STR)
app.include_router(rules.router, prefix=settings.API_V1_STR)
app.include_router(certificates.router, prefix=settings.API_V1_STR)
app.include_router(public_verify.router, prefix=settings.API_V1_STR)
app.include_router(ocr.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)

from fastapi.responses import FileResponse
from fastapi import HTTPException

# Locate bundled frontend if available
FRONTEND_DIST_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "static",
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
    Path("frontend/dist"),
    Path("../frontend/dist"),
    Path("backend/static"),
]
FRONTEND_DIST = next((d for d in FRONTEND_DIST_CANDIDATES if (d / "index.html").exists()), None)

if FRONTEND_DIST and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    if FRONTEND_DIST and (FRONTEND_DIST / "index.html").exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return {
        "project": "LegalMet Verify",
        "status": "ONLINE",
        "docs_url": "/docs",
        "public_verification_url": "/api/public/verify/{certificate_number}"
    }

@app.get("/{full_path:path}")
def serve_frontend_spa(full_path: str):
    if full_path.startswith("api") or full_path.startswith("storage") or full_path.startswith("docs") or full_path == "openapi.json":
        raise HTTPException(status_code=404, detail="Not Found")
    if FRONTEND_DIST:
        target = FRONTEND_DIST / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")
    raise HTTPException(status_code=404, detail="Not Found")

