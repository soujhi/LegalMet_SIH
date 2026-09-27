# Architecture & Technical Design Document

## 1. System Overview
LegalMet Verify follows a **Modular Monolith** architecture designed for high maintainability, rapid deployment, and deterministic execution.

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Tailwind Frontend                   │
│   (Public Portal • Trader Desk • Admin Center • LMO PWA)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / JSON (JWT Auth)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI REST API Layer                   │
├─────────────────────────────────────────────────────────────┤
│                       Service Modules                       │
│  ├── Auth & RBAC               ├── Deterministic Rule Engine │
│  ├── Instrument Registry       ├── Certificate & QR Engine  │
│  ├── Application Workflow      ├── OCR Ingestion & Validate │
│  ├── Scheduling & Assignment   ├── Audit & Anomaly Engine   │
├─────────────────────────────────────────────────────────────┤
│                    Data Persistence Layer                   │
│  ├── SQLAlchemy ORM (18 Models)                             │
│  ├── SQLite / PostgreSQL Database                           │
│  └── Storage (PDF Certificates, QR Codes, Scanned Uploads)  │
└─────────────────────────────────────────────────────────────┘
```

## 2. Technology Stack
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons + React Router v6
- **Backend API:** FastAPI (Python 3.12+) + Pydantic v2 + Uvicorn
- **ORM & Database:** SQLAlchemy 2.0 with SQLite (local development) and PostgreSQL / Supabase compatibility
- **Document Generation:** ReportLab (Official PDF Certificates) + Python QR Code (Pillow engine)
- **Computer Vision & OCR:** Tesseract OCR (v5.x) + PyMuPDF (fitz) + Pillow
- **Security:** Bcrypt password hashing + Jose JWT session handling + Role-Based Access Control (RBAC)

## 3. Data Layers Separation
1. **Layer A — DoCA Model Approval:** Standard reference catalog of legally approved instrument models, manufacturers, accuracy classes, verification scale intervals ($e$), and capacities.
2. **Layer B — State Field Records:** Historical scanned certificates and portal inspection lists imported from state portals (e.g. Jharkhand e-Legal Metrology Barhi sub-division).
3. **Layer C — Live Platform Records:** Real-time applications, GPS-locked field inspection sessions, deterministic test evaluations, issued certificates, and audit logs.
