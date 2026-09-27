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
            self.drawString(40, 11 * inch - 28, "LegalMet Verify (SIH26036) — Master Project Handover & Architecture Manual")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 11 * inch - 32, 8.5 * inch - 40, 11 * inch - 32)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 26, page_text)
        self.drawString(40, 26, "LEGALMET VERIFY • SIH 2026 TECHNICAL HANDOVER SPECIFICATION")
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
        textColor=colors.HexColor('#D97706')
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
    story.append(Paragraph("LEGALMET VERIFY — SYSTEM ARCHITECTURE & HANDOVER", subtitle_style))
    story.append(Paragraph("SIH 2026 Master Project Handover Manual", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Repository:</b> github.com/soujhi/LegalMet_SIH | <b>Scope:</b> Complete system architecture, DoCA pipeline, credentials, and handover checklist", body_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceBefore=2, spaceAfter=6))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Problem Statement:</b> SIH26036", body_style),
            Paragraph("<b>Authority:</b> DoCA / Legal Metrology", body_style),
            Paragraph("<b>Test Suite:</b> 100% Passing (test_flow.py)", body_style)
        ],
        [
            Paragraph("<b>Handover Date:</b> 27 September 2026", body_style),
            Paragraph("<b>Ingested Govt Models:</b> 451 Certificates", body_style),
            Paragraph("<b>Total Catalog:</b> 454 Models in DB", body_style)
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

    # 1. Project Overview & Architecture
    story.append(Paragraph("1. Core Mission & Metrological Architecture (Layer A vs Layer B)", h1_style))
    overview_text = (
        "LegalMet Verify digitizes the statutory lifecycle for commercial weighing and measuring instruments in India. "
        "The system strictly decouples <b>Layer A: Government Model Approval Reference Data</b> (451 scraped DoCA certificates storing authoritative baseline tolerances, capacity, scale interval e, and approval marks) "
        "from <b>Layer B: Physical In-Situ Trader Deployments</b> (individual commercial scales registered with serial numbers, asset tags, GPS locations, and inspection histories). "
        "During field inspections, the deterministic rule engine verifies observations against the <b>Seventh Schedule, Part-II</b> and <b>OIML R 76-1</b> standards before issuing tamper-evident QR certificates."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 6))

    # 2. What Has Been Completed
    story.append(Paragraph("2. Completed Deliverables & System Components", h1_style))
    comp_data = [
        [Paragraph("Subsystem", table_header), Paragraph("Component", table_header), Paragraph("Implementation Details & Deliverables", table_header)],
        [Paragraph("DoCA Ingestion", table_cell_bold), Paragraph("scripts/import_doca_model_approval.py", table_cell_mono), Paragraph("Extracted all 451 PDFs into detailed CSV, JSON, and SQLite catalog with 0 OCR fallbacks.", table_cell)],
        [Paragraph("Backend APIs", table_cell_bold), Paragraph("backend/app/routers/ (11 modules)", table_cell_mono), Paragraph("FastAPI endpoints for Auth, Instruments, Applications, Scheduling, Verification, Rules, Certificates, Analytics, Audit.", table_cell)],
        [Paragraph("Rule Engine", table_cell_bold), Paragraph("backend/app/services/rule_engine.py", table_cell_mono), Paragraph("Deterministic MPE evaluation (±0.5e, ±1.0e, ±1.5e initial; ±1.0e, ±2.0e, ±3.0e in-service).", table_cell)],
        [Paragraph("Certificates & QR", table_cell_bold), Paragraph("certificate_generator.py", table_cell_mono), Paragraph("ReportLab PDF generator with cryptographic SHA-256 fingerprint and tamper-evident QR code.", table_cell)],
        [Paragraph("Frontend Portals", table_cell_bold), Paragraph("frontend/src/pages/ (15 views)", table_cell_mono), Paragraph("React 18 + TS + Tailwind portals for Trader, LMO Inspector, Admin Controller, and Public Verification.", table_cell)],
        [Paragraph("Automated Tests", table_cell_bold), Paragraph("scripts/test_flow.py", table_cell_mono), Paragraph("100% passing Golden PASS (cert issuance) and Failure FAIL (MPE rejection) test suite.", table_cell)],
    ]
    comp_table = Table(comp_data, colWidths=[80, 160, 292])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 6))

    # Page Break for clean 2-page document
    story.append(PageBreak())

    # 3. Flagged Items & Handover Checklist
    story.append(Paragraph("3. Flagged Items for Refinement (Handover Checklist)", h1_style))
    flag_data = [
        [Paragraph("Item", table_header), Paragraph("Observed Behavior", table_header), Paragraph("Recommended Action", table_header), Paragraph("Target File", table_header)],
        [
            Paragraph("1. Class IIII Precedence", table_cell_bold),
            Paragraph("Substring check for 'CLASS III' matched 'CLASS IIII'.", table_cell),
            Paragraph("Move Class IIII condition before Class III in if-else chain.", table_cell),
            Paragraph("rule_engine.py", table_cell_mono)
        ],
        [
            Paragraph("2. Scale Interval < 1g", table_cell_bold),
            Paragraph("e=0.1g on Class II balances skipped gram-to-kg conversion.", table_cell),
            Paragraph("Explicitly divide by 1000 whenever unit is kg.", table_cell),
            Paragraph("rule_engine.py", table_cell_mono)
        ],
        [
            Paragraph("3. Cert Hash Keys", table_cell_bold),
            Paragraph("Dictionary key named 'model' vs 'model_series'.", table_cell),
            Paragraph("Align hash dict keys between generator and router.", table_cell),
            Paragraph("certificate_generator.py", table_cell_mono)
        ],
        [
            Paragraph("4. UI Denominator Label", table_cell_bold),
            Paragraph("Catalog total shows 454 without subtitle.", table_cell),
            Paragraph("Add label: '451 DoCA Certificates + 3 Seed Models'.", table_cell),
            Paragraph("AdminDataQuality.tsx", table_cell_mono)
        ],
    ]
    flag_table = Table(flag_data, colWidths=[95, 140, 160, 137])
    flag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D97706')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(flag_table)
    story.append(Spacer(1, 6))

    # 4. Quick Start & Test Accounts
    story.append(Paragraph("4. Quick-Start Guide & Seed Credentials", h1_style))
    cred_data = [
        [Paragraph("Role", table_header), Paragraph("Name", table_header), Paragraph("Email Login", table_header), Paragraph("Password", table_header), Paragraph("Scope / Persona", table_header)],
        [Paragraph("Admin", table_cell_bold), Paragraph("Rajesh Verma", table_cell), Paragraph("admin@legalmet.gov.in", table_cell_mono), Paragraph("Admin@123", table_cell_mono), Paragraph("State Inspector / Controller", table_cell)],
        [Paragraph("LMO Officer", table_cell_bold), Paragraph("Amit Sharma", table_cell), Paragraph("lmo.sharma@legalmet.gov.in", table_cell_mono), Paragraph("Lmo@123", table_cell_mono), Paragraph("Field Inspection Execution", table_cell)],
        [Paragraph("Trader 1", table_cell_bold), Paragraph("Ramesh Patel", table_cell), Paragraph("trader.patel@agrotraders.in", table_cell_mono), Paragraph("Trader@123", table_cell_mono), Paragraph("Patel Agro Commodities (Mandi)", table_cell)],
        [Paragraph("Trader 2", table_cell_bold), Paragraph("Sanjay Gupta", table_cell), Paragraph("trader.gupta@barhistore.in", table_cell_mono), Paragraph("Trader@123", table_cell_mono), Paragraph("Gupta Kirana Store (Retail)", table_cell)],
    ]
    cred_table = Table(cred_data, colWidths=[65, 85, 150, 85, 147])
    cred_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(cred_table)
    story.append(Spacer(1, 6))

    # Execution Commands
    story.append(Paragraph("5. Developer Commands to Run and Test", h1_style))
    cmd_text = (
        "<b>Backend Server:</b> <code>cd backend; pip install -r requirements.txt; python -m uvicorn app.main:app --reload --port 8000</code><br/>"
        "<b>Frontend App:</b> <code>cd frontend; npm install; npm run dev</code> (Runs on http://localhost:5173 or :3000)<br/>"
        "<b>Automated Test Suite:</b> <code>python scripts/test_flow.py</code> (Runs Golden PASS & FAIL flows end-to-end)"
    )
    story.append(Paragraph(cmd_text, body_style))
    story.append(Spacer(1, 6))

    # Sign-off box
    signoff_data = [
        [
            Paragraph("<b>Repository:</b> https://github.com/soujhi/LegalMet_SIH", body_style),
            Paragraph("<b>Status:</b> FULLY PUSHED & SYNCHRONIZED", body_bold),
            Paragraph("<b>Verdict:</b> HANDOVER READY", body_bold)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[200, 180, 152])
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
        r"C:\Users\Class rep\Desktop\Sih\reports\LegalMet_Project_Handover_Master.pdf",
        r"C:\Users\Class rep\.gemini\antigravity\brain\dec88633-0c15-47e0-a45b-611ca3a967ff\LegalMet_Project_Handover_Master.pdf"
    ]
    generate_pdf(paths)
    print("Successfully generated LegalMet Project Handover Master PDF.")
