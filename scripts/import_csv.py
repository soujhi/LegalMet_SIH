import csv
import json
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.models import OCRDocument, InstrumentModel, SourceProvenance

def import_legacy_data(csv_path: Path):
    db = SessionLocal()
    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                doc = OCRDocument(
                    source_file=row.get("source_file", "scanned_cert.pdf"),
                    certificate_no=row.get("certificate_no"),
                    area=row.get("area", "BARHI"),
                    concern_name=row.get("concern_name", "Commercial Trader"),
                    verification_date=row.get("verification_date", "01/04/2024"),
                    next_verification_date=row.get("next_verification_date", "31/03/2025"),
                    instrument_type=row.get("instrument_type", "Non-Automatic Weighing Instrument"),
                    manufacturer=row.get("manufacturer", "Standard Scale"),
                    model=row.get("model", "Commercial Counter Scale"),
                    capacity=row.get("capacity", "30 kg"),
                    accuracy_class=row.get("accuracy_class", "Class III"),
                    verification_fee=row.get("verification_fee", "Rs. 250/-"),
                    raw_ocr_text=row.get("raw_ocr_text", ""),
                    ocr_confidence=float(row.get("ocr_confidence", 85.0)),
                    manual_verified=row.get("manual_verified", "False").lower() == "true",
                    source_type=SourceProvenance.OCR
                )
                db.add(doc)
                count += 1
            db.commit()
            print(f"Successfully imported {count} legacy records from CSV into database.")
    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    sample_csv = base_dir / "data" / "processed" / "legal_metrology_ocr.csv"
    if sample_csv.exists():
        import_legacy_data(sample_csv)
    else:
        print("CSV file not found at data/processed/legal_metrology_ocr.csv")
