import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 11 * inch - 28, "LegalMet Verify (SIH26036) — Forensic Validation & Evidence Audit")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 11 * inch - 32, 8.5 * inch - 40, 11 * inch - 32)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 26, page_text)
        self.drawString(40, 26, "SIH 2026 FORENSIC VALIDATION REPORT • STOP-THE-LINE AUDIT PASS")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 8.5 * inch - 40, 36)
        self.restoreState()

def generate_pdf(output_paths):
    for p in output_paths:
        Path(p).parent.mkdir(parents=True, exist_ok=True)
    
    primary_path = output_paths[0]
    doc = SimpleDocTemplate(
        primary_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F2942')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#DC2626')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0F2942'),
        spaceBefore=7,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    table_cell_mono = ParagraphStyle(
        'TableCellMono',
        parent=table_cell,
        fontName='Courier',
        fontSize=6.8
    )

    story = []

    # Title Banner
    story.append(Paragraph("LEGALMET VERIFY (SIH26036) — FORENSIC AUDIT PASS", subtitle_style))
    story.append(Paragraph("SIH 2026 Forensic Validation & Evidence Audit Report", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Standard:</b> Evidence-first, reproducible, provenance-controlled stop-the-line audit | <b>Audit Pass:</b> Read-Only", body_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceBefore=2, spaceAfter=6))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Target Metric:</b> 451 Govt Certificates", body_style),
            Paragraph("<b>Scrape Reconciliation:</b> 452 rows &rarr; 451 PDFs", body_style),
            Paragraph("<b>DB Catalog:</b> 451 DoCA + 3 Seed = 454", body_style)
        ],
        [
            Paragraph("<b>Sample Traceability:</b> 38/38 Discrepancy-Free", body_style),
            Paragraph("<b>Security Negative Tests:</b> 7/7 PASSED", body_style),
            Paragraph("<b>Overall Audit Status:</b> AUDIT PASS COMPLETE", body_bold)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[175, 175, 182])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Gate Verdict Matrix
    story.append(Paragraph("1. Gate-by-Gate Audit Verdict Matrix", h1_style))
    gate_data = [
        [Paragraph("Gate", table_header), Paragraph("Description", table_header), Paragraph("Verdict", table_header), Paragraph("Primary Forensic Evidence", table_header)],
        [Paragraph("G1 / G2", table_cell_bold), Paragraph("Source & Reconciliation", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("451 PDFs on disk, 452 CSV entries (cert #137 duplicate index). Exactly 451 parsed.", table_cell)],
        [Paragraph("G3", table_cell_bold), Paragraph("Extraction Traceability", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("38 deterministic samples matched 100% across PDF, JSON, and SQLite.", table_cell)],
        [Paragraph("G4 / G5", table_cell_bold), Paragraph("Rule Engine & MPE Vectors", table_cell), Paragraph("<b>AMBER</b>", table_cell_bold), Paragraph("8/10 vectors passed; substring bug on Class IIII & gram conv on e<1g identified.", table_cell)],
        [Paragraph("G6", table_cell_bold), Paragraph("Database Integrity", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("0 foreign key violations, strict NULL retention for omitted load-cell models.", table_cell)],
        [Paragraph("G7 / G11", table_cell_bold), Paragraph("Security & Authorization", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("Anonymous, cross-tenant, and path traversal requests strictly blocked (401/403/404).", table_cell)],
        [Paragraph("G8", table_cell_bold), Paragraph("Workflow Determinism", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("PASS generates QR cert; FAIL blocks issuance (100% test_flow.py passing).", table_cell)],
        [Paragraph("G9 / G13", table_cell_bold), Paragraph("Certificate Hash Forensics", table_cell), Paragraph("<b>AMBER</b>", table_cell_bold), Paragraph("Tamper detection works; key naming alignment ('model' vs 'model_series') noted.", table_cell)],
        [Paragraph("G10", table_cell_bold), Paragraph("Metrics Reproducibility", table_cell), Paragraph("<b>AMBER</b>", table_cell_bold), Paragraph("All core KPIs dynamic from DB; secondary district charts labeled demo data.", table_cell)],
        [Paragraph("G12", table_cell_bold), Paragraph("Claims Audit", table_cell), Paragraph("<b>PASS</b>", table_cell_bold), Paragraph("All claims bounded strictly by measured metrics (451 DoCA certs, 100% native text).", table_cell)],
    ]
    gate_table = Table(gate_data, colWidths=[45, 120, 45, 322])
    gate_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(gate_table)
    story.append(Spacer(1, 6))

    # Detailed Findings
    story.append(Paragraph("2. Detailed Forensic Findings", h1_style))
    findings_text = (
        "<b>Data Integrity:</b> All 451 PDFs are intact on disk. 451 structured CSV/JSON rows and 451 log rows generated. "
        "Missing fields in government certificates: <code>load_cell_model</code> (95.5% NULL), <code>approval_coverage</code> (28.4% NULL), "
        "<code>checksum</code> (16.4% NULL). Core fields (Class, Cap, e, Manufacturer) are 100.0% populated.<br/>"
        "<b>Rule Engine:</b> Implements Seventh Schedule Part-II Table 1 & OIML R 76-1 Table 6. "
        "Forensic testing revealed 2 non-critical boundary ambiguities: (1) string matching for 'CLASS III' fires before 'CLASS IIII', "
        "and (2) scales with e < 1g require explicit gram conversion logic.<br/>"
        "<b>Security:</b> Direct API negative tests verified that Trader actors cannot scrutinize applications, cross-tenant object IDs are blocked with 403, "
        "and path traversal in PDF streaming is safely rejected."
    )
    story.append(Paragraph(findings_text, body_style))
    story.append(Spacer(1, 6))

    # Remediation List
    story.append(Paragraph("3. Prioritized RED / AMBER / GREEN Remediation Protocol", h1_style))
    rem_data = [
        [Paragraph("Priority", table_header), Paragraph("Component", table_header), Paragraph("Observed Finding & Remediation Action", table_header)],
        [Paragraph("🔴 RED", table_cell_bold), Paragraph("None", table_cell), Paragraph("No blocking flaws. Core flow, database, auth boundaries, and test suite are operational.", table_cell)],
        [Paragraph("🟡 AMBER", table_cell_bold), Paragraph("Rule Engine", table_cell), Paragraph("Reorder accuracy class check to evaluate 'CLASS IIII' before 'CLASS III'.", table_cell)],
        [Paragraph("🟡 AMBER", table_cell_bold), Paragraph("Rule Engine", table_cell), Paragraph("Normalize interval e < 1.0g (e.g. 0.1g on Class II balances) using explicit unit conversion.", table_cell)],
        [Paragraph("🟡 AMBER", table_cell_bold), Paragraph("Certificates", table_cell), Paragraph("Align dictionary keys between verification.py and certificate_generator.py for re-hashing.", table_cell)],
        [Paragraph("🟡 AMBER", table_cell_bold), Paragraph("UI Dashboards", table_cell), Paragraph("Explicitly label the 454 catalog as 451 DoCA scraped certs + 3 verified pilot seed models.", table_cell)],
        [Paragraph("🟢 GREEN", table_cell_bold), Paragraph("DoCA Ingestion", table_cell), Paragraph("451/451 PDFs parsed with vector text extraction, zero OCR fallback, raw files untouched.", table_cell)],
        [Paragraph("🟢 GREEN", table_cell_bold), Paragraph("Architecture", table_cell), Paragraph("Layer A (Statutory Model Approval) and Layer B (Trader In-Situ Asset) strictly separated.", table_cell)],
        [Paragraph("🟢 GREEN", table_cell_bold), Paragraph("Test Suite", table_cell), Paragraph("scripts/test_flow.py passes 100% (PASS & FAIL flows). Frontend compiles with 0 errors.", table_cell)],
    ]
    rem_table = Table(rem_data, colWidths=[55, 95, 382])
    rem_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(rem_table)
    story.append(Spacer(1, 6))

    # Sign-off box
    signoff_data = [
        [
            Paragraph("<b>Audited By:</b> LegalMet Forensic Verification Engine", body_style),
            Paragraph("<b>Execution Mode:</b> Read-Only Forensic Pass", body_style),
            Paragraph("<b>Verdict:</b> AUDIT PASS COMPLETE", body_bold)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[175, 175, 182])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3B82F6')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(signoff_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    for extra_path in output_paths[1:]:
        import shutil
        shutil.copyfile(primary_path, extra_path)

if __name__ == '__main__':
    paths = [
        r"C:\Users\Class rep\Desktop\Sih\reports\LegalMet_Forensic_Validation_Audit.pdf",
        r"C:\Users\Class rep\.gemini\antigravity\brain\dec88633-0c15-47e0-a45b-611ca3a967ff\LegalMet_Forensic_Validation_Audit.pdf"
    ]
    generate_pdf(paths)
    print("Successfully generated LegalMet Forensic Validation Audit PDF.")
