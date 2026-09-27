import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://lm.doca.gov.in/modelapproval/Certificates.aspx"

OUTPUT_DIR = "data/government/doca_model_approval"
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
CSV_FILE = os.path.join(OUTPUT_DIR, "doca_model_approval.csv")

os.makedirs(PDF_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(headers)

print("Opening DoCA Model Approval page...")

response = session.get(BASE_URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

rows = []

table = soup.find("table")

if not table:
    print("Could not find certificate table.")
    exit()

for tr in table.find_all("tr"):
    cells = tr.find_all(["td", "th"])

    if len(cells) < 7:
        continue

    values = [cell.get_text(" ", strip=True) for cell in cells]

    if values[0].lower() in ["serial no.", "serial no"]:
        continue

    link = tr.find("a", href=True)

    pdf_url = ""

    if link:
        pdf_url = urljoin(BASE_URL, link["href"])

    rows.append({
        "serial_no": values[0],
        "issue_date": values[1],
        "file_number": values[2],
        "company_name": values[3],
        "equipment": values[4],
        "certificate_no": values[5],
        "online_application_no": values[6],
        "pdf_url": pdf_url,
        "source": "DOCA_MODEL_APPROVAL"
    })

print(f"Found {len(rows)} certificate records.")

fieldnames = [
    "serial_no",
    "issue_date",
    "file_number",
    "company_name",
    "equipment",
    "certificate_no",
    "online_application_no",
    "pdf_url",
    "source"
]

with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV saved to: {CSV_FILE}")

print("\nDownloading PDFs...\n")

for i, row in enumerate(rows, 1):

    pdf_url = row["pdf_url"]

    if not pdf_url:
        print(f"[{i}/{len(rows)}] No PDF link: {row['certificate_no']}")
        continue

    certificate_no = row["certificate_no"]

    safe_name = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in certificate_no
    )

    output_file = os.path.join(
        PDF_DIR,
        f"{safe_name}.pdf"
    )

    if os.path.exists(output_file):
        print(f"[{i}/{len(rows)}] Already exists: {certificate_no}")
        continue

    try:
        r = session.get(pdf_url, timeout=60)

        if r.status_code == 200 and r.content[:4] == b"%PDF":

            with open(output_file, "wb") as f:
                f.write(r.content)

            print(f"[{i}/{len(rows)}] Downloaded: {certificate_no}")

        else:
            print(
                f"[{i}/{len(rows)}] Failed: "
                f"{certificate_no} | HTTP {r.status_code}"
            )

    except Exception as e:
        print(f"[{i}/{len(rows)}] Error: {certificate_no} | {e}")

    time.sleep(0.3)

print("\nDONE")
print(f"Metadata: {CSV_FILE}")
print(f"PDFs: {PDF_DIR}")