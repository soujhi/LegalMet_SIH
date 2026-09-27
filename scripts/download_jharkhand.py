from html.parser import HTMLParser
import json
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.in_link = False
        self.cell_text = []
        self.cells = []
        self.href = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "table" and attrs.get("id") == "ContentPlaceHolder1_DvView":
            self.in_table = True

        elif self.in_table and tag == "tr":
            self.in_row = True
            self.cells = []

        elif self.in_table and self.in_row and tag == "td":
            self.in_cell = True
            self.cell_text = []

        elif self.in_table and self.in_row and tag == "a":
            self.in_link = True
            self.href = attrs.get("href")

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_link = False

        elif tag == "td" and self.in_cell:
            self.in_cell = False
            text = " ".join("".join(self.cell_text).split())
            self.cells.append((text, self.href))
            self.href = None

        elif tag == "tr" and self.in_row:
            self.in_row = False
            if len(self.cells) >= 4:
                self.rows.append(self.cells)

        elif tag == "table" and self.in_table:
            self.in_table = False

    def handle_data(self, data):
        if self.in_cell:
            self.cell_text.append(data)

parser = Parser()

with open("Untitled-1.html", "r", encoding="utf-8", errors="ignore") as f:
    parser.feed(f.read())

records = []

for cells in parser.rows:
    pdf_cell, area_cell, cert_cell, concern_cell = cells[:4]
    href = pdf_cell[1]

    if href:
        if href.startswith("../"):
            href = href[3:]

        pdf_url = "https://elegalmetrology.jharkhand.gov.in/" + href.lstrip("/")

        records.append({
            "area": area_cell[0],
            "certificate_no": cert_cell[0],
            "concern_name": concern_cell[0],
            "pdf_url": pdf_url
        })

with open("jharkhand_barhi_certificates.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Found {len(records)} records.")
print("JSON created successfully.")

os.makedirs("pdfs", exist_ok=True)

for i, item in enumerate(records, 1):
    url = item["pdf_url"]
    cert = item["certificate_no"]
    filename = f"{i}_{cert}.pdf"
    path = os.path.join("pdfs", filename)

    try:
        r = requests.get(url, timeout=30,  verify=False)

        if r.status_code == 200 and r.content[:4] == b"%PDF":
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"[{i}/{len(records)}] ✓ {filename}")
        else:
            print(f"[{i}/{len(records)}] ✗ {cert} - HTTP {r.status_code}")

    except Exception as e:
        print(f"[{i}/{len(records)}] ✗ {cert} - {e}")

print("Finished.")