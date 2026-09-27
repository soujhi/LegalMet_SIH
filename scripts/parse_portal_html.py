import json
from html.parser import HTMLParser
from pathlib import Path

class JharkhandPortalParser(HTMLParser):
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
        attrs_dict = dict(attrs)
        if tag == "table" and attrs_dict.get("id") == "ContentPlaceHolder1_DvView":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.cells = []
        elif self.in_table and self.in_row and tag == "td":
            self.in_cell = True
            self.cell_text = []
        elif self.in_table and self.in_row and tag == "a":
            self.in_link = True
            self.href = attrs_dict.get("href")

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

def parse_html_to_records(html_path: Path) -> list:
    parser = JharkhandPortalParser()
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
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
    return records

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    raw_html = base_dir / "data" / "government" / "jharkhand" / "portal_barhi_raw.html"
    out_json = base_dir / "data" / "government" / "jharkhand" / "jharkhand_barhi_certificates.json"

    if raw_html.exists():
        recs = parse_html_to_records(raw_html)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False, indent=2)
        print(f"Parsed {len(recs)} government certificate records into {out_json}")
    else:
        print(f"Raw HTML not found at {raw_html}")
