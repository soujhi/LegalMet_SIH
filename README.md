# LegalMet Verify (SIH26036)
### Online Verification System for Weighing and Measuring Instruments

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Compliance](https://img.shields.io/badge/Legal%20Metrology-Act%202009-EA580C.svg?style=flat)](https://consumeraffairs.nic.in)

LegalMet Verify is a full-stack digital lifecycle management system for weighing and measuring instruments under the **Legal Metrology Act, 2009** and **Legal Metrology (General) Rules, 2011**.

---

## 🌟 Core Features & Architecture

- **Trader Portal:** Instrument catalog linked with Central DoCA Model Approvals, verification & re-verification filing, application tracking timeline, and certificate vault.
- **Admin Control Center:** Application scrutiny (Approve / Query / Reject), officer scheduling, district analytics, and immutable audit logs.
- **Mobile-First LMO Field App:** Field inspections with GPS coordinates lock, device timestamping, photo evidence, test load observations, and instant PASS/FAIL evaluation.
- **Deterministic Regulatory Rule Engine:** Codified step-function Maximum Permissible Error (MPE) calculations for Accuracy Class I, II, III, and IIII without AI hallucination.
- **Verifiable Digital Certificates:** Generates tamper-proof PDF certificates with SHA-256 cryptographic fingerprints and QR codes linking to public verification.
- **Public QR Verification:** Instant public authentication of certificates without login, displaying validity, capacity, class, and authorized officer.
- **Legacy OCR Digitization Hub:** Ingestion of state government inspection scans (Jharkhand Barhi dataset) with confidence scoring and human-in-the-loop validation.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m app.db_init
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000`. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Portal will run at `http://localhost:3000`.

---

## 🔑 Demo Accounts & Golden Workflow

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Trader** | `trader.patel@agrotraders.in` | `Trader@123` | Patel Agro Commodities & Seeds (Barhi) |
| **Admin** | `admin@legalmet.gov.in` | `Admin@123` | Senior Legal Metrology Inspector |
| **LMO Officer** | `lmo.sharma@legalmet.gov.in` | `Lmo@123` | Amit Sharma (`LMO-JH-001`), Barhi Jurisdiction |

> **Tip:** You can switch between roles in one click using the **Demo Switcher** in the top navigation bar.

### Golden Demo Flow:
1. **Trader:** Login $\rightarrow$ My Instruments $\rightarrow$ Apply for Re-Verification $\rightarrow$ Submit.
2. **Admin:** Scrutiny $\rightarrow$ Approve $\rightarrow$ Assign LMO Officer (`LMO-JH-001`) & set schedule.
3. **LMO:** Open field inspection $\rightarrow$ Lock GPS $\rightarrow$ Select **Preset PASS** $\rightarrow$ Evaluate & Submit.
4. **Certificate & QR:** Certificate generated with QR code pointing to `/verify/{certificate_number}`.
5. **Public:** Scan QR or open link $\rightarrow$ See **CERTIFICATE VALID & VERIFIED** status.

---

## 📁 Repository Layout
```
├── backend/
│   ├── app/
│   │   ├── core/         # Config, Database, JWT Security
│   │   ├── models/       # SQLAlchemy ORM (18 Models)
│   │   ├── schemas/      # Pydantic Schemas
│   │   ├── services/     # Rule Engine, Certificate Generator, OCR, Audit
│   │   ├── routers/      # REST API Routers
│   │   ├── db_init.py    # Database schema creator & seed loader
│   │   └── main.py       # FastAPI Entry point
│   ├── storage/          # Generated Certificates, QR Codes, and Uploads
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Public, Trader, Admin, and LMO Pages
│   │   ├── components/   # Navbar, StatusBadge, UI widgets
│   │   ├── context/      # Authentication & Quick-Login Context
│   │   ├── api/          # Typed API Client
│   │   └── types/        # TypeScript Interfaces
│   ├── package.json
│   └── vite.config.ts
├── database/
│   ├── schema.sql        # Database schema definition
│   └── legalmet.db       # Persistent SQLite Database
├── data/
│   ├── government/       # Jharkhand Portal HTML, JSON, and OCR data
│   │   └── jharkhand/
│   └── processed/        # Processed CSVs
├── scripts/
│   ├── download_jharkhand.py
│   ├── parse_portal_html.py
│   ├── ocr_certificates.py
│   └── import_csv.py
└── docs/
    ├── PRD.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DATA_DICTIONARY.md
    ├── DATA_PROVENANCE.md
    ├── REGULATORY_RULES.md
    ├── OCR_PIPELINE.md
    ├── DEMO_SCRIPT.md
    └── KNOWN_LIMITATIONS.md
```
