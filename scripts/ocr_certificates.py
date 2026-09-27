import os
import re
import fitz
import pytesseract
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PDF_FOLDER = "pdfs"
OUTPUT_CSV = "legal_metrology_ocr.csv"
RAW_FOLDER = "ocr_text"

os.makedirs(RAW_FOLDER, exist_ok=True)

def preprocess(image):
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2)
    image = ImageEnhance.Sharpness(image).enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image

def extract_certificate_number(filename, text):
    match = re.search(r'(\d{6})', filename)

    if match:
        return match.group(1)

    numbers = re.findall(r'\b\d{6}\b', text)

    return numbers[0] if numbers else ""

def extract_dates(text):
    patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b'
    ]

    dates = []

    for pattern in patterns:
        dates.extend(re.findall(pattern, text))

    return list(dict.fromkeys(dates))

def get_ocr(image):
    data = pytesseract.image_to_data(
        image,
        lang="hin+eng",
        config="--psm 6",
        output_type=Output.DICT
    )

    words = []
    confidences = []

    for word, conf in zip(data["text"], data["conf"]):
        word = word.strip()

        try:
            conf = float(conf)
        except:
            conf = -1

        if word:
            words.append(word)

        if conf >= 0:
            confidences.append(conf)

    text = " ".join(words)

    confidence = (
        round(sum(confidences) / len(confidences), 2)
        if confidences else 0
    )

    return text, confidence

records = []

pdf_files = sorted(
    [
        f for f in os.listdir(PDF_FOLDER)
        if f.lower().endswith(".pdf")
    ],
    key=lambda x: int(re.search(r'^(\d+)', x).group(1))
    if re.search(r'^(\d+)', x)
    else 999999
)

print(f"Found {len(pdf_files)} PDF files.")
print()

for index, filename in enumerate(pdf_files, 1):

    print(f"[{index}/{len(pdf_files)}] Processing {filename}")

    path = os.path.join(PDF_FOLDER, filename)

    try:
        doc = fitz.open(path)

        full_text = ""
        confidence_values = []

        for page in doc:

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2.5, 2.5),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            image = preprocess(image)

            text, confidence = get_ocr(image)

            full_text += text + "\n"
            confidence_values.append(confidence)

        doc.close()

        certificate_no = extract_certificate_number(
            filename,
            full_text
        )

        dates = extract_dates(full_text)

        avg_confidence = (
            round(
                sum(confidence_values) /
                len(confidence_values),
                2
            )
            if confidence_values else 0
        )

        raw_filename = os.path.splitext(filename)[0] + ".txt"

        with open(
            os.path.join(RAW_FOLDER, raw_filename),
            "w",
            encoding="utf-8"
        ) as f:
            f.write(full_text)

        records.append({
            "source_file": filename,
            "certificate_no": certificate_no,
            "verification_dates_found": " | ".join(dates),
            "raw_ocr_text": full_text.replace("\n", " "),
            "ocr_confidence": avg_confidence,
            "manual_verified": False
        })

        print(
            f"   Certificate: {certificate_no} | "
            f"Confidence: {avg_confidence}%"
        )

    except Exception as e:

        print(f"   ERROR: {e}")

        records.append({
            "source_file": filename,
            "certificate_no": "",
            "verification_dates_found": "",
            "raw_ocr_text": "",
            "ocr_confidence": 0,
            "manual_verified": False
        })

df = pd.DataFrame(records)

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print()
print("===================================")
print("OCR COMPLETE")
print("===================================")
print(f"CSV: {OUTPUT_CSV}")
print(f"Raw OCR: {RAW_FOLDER}/")
print(f"Records: {len(df)}")