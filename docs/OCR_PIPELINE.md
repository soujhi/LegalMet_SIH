# Legacy OCR Digitization Pipeline

## 1. Pipeline Overview
The OCR module processes legacy scanned certificate PDFs (e.g. from the Jharkhand e-Legal Metrology Portal) using an assisted digitization workflow:

```
[Scanned PDF / Image]
         ↓
[PyMuPDF Vector Rasterization (2.5x Resolution Matrix)]
         ↓
[Image Preprocessing (Grayscale + Contrast Enhance + Sharpen Filter)]
         ↓
[Tesseract OCR Engine (English + Hindi langpacks, PSM 6 / PSM 3)]
         ↓
[Regex Heuristic Field Extraction (Certificate No, Dates, Capacity, Fee, Concern)]
         ↓
[Confidence Score Computation (Word confidence + Key template tokens)]
         ↓
[Ingestion into Database (manual_verified = FALSE)]
         ↓
[Admin / LMO Side-by-Side Validation Interface]
         ↓
[Officer Approves Corrections → manual_verified = TRUE]
```

## 2. Key Heuristic Extractors
- **Certificate Number:** Searches 6-digit integer patterns matching state portal nomenclature.
- **Verification Dates:** Identifies `DD/MM/YYYY`, `DD-MM-YYYY`, and `DD.MM.YYYY` patterns.
- **Accuracy Class & Capacity:** Extracts metric capacity (`kg`, `g`, `quintal`) and accuracy classes (`Class III`, `Class IIII`).
- **Confidence Scoring:** Calculates token match density against standard legal metrology template vocabulary (`verification`, `certificate`, `metrology`, `capacity`, `class`, `fee`).
