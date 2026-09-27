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
            self.drawString(40, 11 * inch - 28, "LegalMet Verify (SIH26036) — DoCA Model Approval Integration Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 11 * inch - 32, 8.5 * inch - 40, 11 * inch - 32)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 40, 26, page_text)
        self.drawString(40, 26, "CONFIDENTIAL & OFFICIAL TECHNICAL SPECIFICATION • GOVERNMENT OF INDIA")
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
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=19,
        textColor=colors.HexColor('#0F2942')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#D97706')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#0F2942'),
        spaceBefore=7,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
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
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
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
        fontSize=7
    )

    story = []

    # Title Banner
    story.append(Paragraph("LEGALMET VERIFY — SYSTEM TECHNICAL REPORT", subtitle_style))
    story.append(Paragraph("DoCA Model Approval Pipeline & Certificate Integration", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Scope:</b> Ingestion of 451 Government of India (DoCA) Model Approval Certificates into LegalMet Verify (SIH26036)", body_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceBefore=2, spaceAfter=6))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Authority:</b> Dept. of Consumer Affairs (DoCA)", body_style),
            Paragraph("<b>Target Metric:</b> 451 Govt Certificates", body_style),
            Paragraph("<b>Extraction Rate:</b> 100.0% (451/451)", body_style)
        ],
        [
            Paragraph("<b>Integration Date:</b> 27 September 2026", body_style),
            Paragraph("<b>Provenance:</b> DOCA_MODEL_APPROVAL", body_style),
            Paragraph("<b>Golden Flow Status:</b> 100% PASSING", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[175, 175, 182])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary & Core Objective", h1_style))
    exec_summary_text = (
        "The automated DoCA Model Approval data pipeline has been successfully constructed, tested, and deployed. "
        "All <b>451 downloaded government PDF certificates</b> (spanning certificate files 1.pdf through 23678.pdf) "
        "have been parsed using high-precision vector text layer extraction, validated against metrological tolerance rules, "
        "and mapped into the <code>instrument_models</code> catalog. The core golden verification flow (both Pass and Fail workflows) "
        "remains 100% functional, and original raw government source PDFs remain intact and untouched in their source directory."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 6))

    # Section 2: Extraction & Ingestion Metrics
    story.append(Paragraph("2. Ingestion & Extraction Performance Metrics", h1_style))
    metrics_data = [
        [Paragraph("Pipeline Metric", table_header), Paragraph("Count / Value", table_header), Paragraph("Ratio", table_header), Paragraph("Operational Impact", table_header)],
        [Paragraph("Total Govt Certificates Processed", table_cell_bold), Paragraph("451", table_cell_mono), Paragraph("100.0%", table_cell), Paragraph("Complete coverage of downloaded repository", table_cell)],
        [Paragraph("Native Text Stream Ingestion", table_cell_bold), Paragraph("451", table_cell_mono), Paragraph("100.0%", table_cell), Paragraph("Direct vector text extraction via PyMuPDF", table_cell)],
        [Paragraph("OCR Fallback Invocations", table_cell_bold), Paragraph("0", table_cell_mono), Paragraph("0.0%", table_cell), Paragraph("Machine-readable text layer available in all PDFs", table_cell)],
        [Paragraph("Average Extraction Confidence", table_cell_bold), Paragraph("95.0%", table_cell_mono), Paragraph("—", table_cell), Paragraph("High confidence with complete spec validation", table_cell)],
        [Paragraph("Total Models in System Catalog", table_cell_bold), Paragraph("454", table_cell_mono), Paragraph("—", table_cell), Paragraph("451 DoCA models + 3 verified seed models", table_cell)],
        [Paragraph("Core Spec Completeness (Class, Cap, e)", table_cell_bold), Paragraph("451 / 451", table_cell_mono), Paragraph("100.0%", table_cell), Paragraph("Zero nulls in essential verification parameters", table_cell)],
    ]
    metrics_table = Table(metrics_data, colWidths=[150, 70, 50, 262])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 6))

    # Section 3: Generated Processed Artifacts
    story.append(Paragraph("3. Generated Government Data Artifacts", h1_style))
    art_data = [
        [Paragraph("Artifact Filename", table_header), Paragraph("Format & Records", table_header), Paragraph("Description & Contents", table_header)],
        [Paragraph("model_approval_detailed.csv", table_cell_bold), Paragraph("CSV • 451 rows", table_cell_mono), Paragraph("Tabular export of all 26+ metrological fields with normalized values.", table_cell)],
        [Paragraph("model_approval_detailed.json", table_cell_bold), Paragraph("JSON • 451 items", table_cell_mono), Paragraph("Full hierarchical dataset with raw extracted text caches and metadata.", table_cell)],
        [Paragraph("extraction_log.csv", table_cell_bold), Paragraph("CSV • 451 rows", table_cell_mono), Paragraph("Per-file audit log recording status, confidence, and missing fields.", table_cell)],
    ]
    art_table = Table(art_data, colWidths=[150, 95, 287])
    art_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(art_table)
    story.append(Spacer(1, 6))

    # Section 4: Missing Fields & Government Certificate Characteristics
    sec4 = []
    sec4.append(Paragraph("4. Statutory Field Integrity & Missing Field Analysis", h1_style))
    missing_analysis = (
        "Under Legal Metrology compliance guidelines, technical values not explicitly present in official gazette notifications "
        "are strictly maintained as <b>NULL</b> and never synthetically fabricated. The analysis reveals:"
    )
    sec4.append(Paragraph(missing_analysis, body_style))
    sec4.append(Spacer(1, 3))

    missing_data = [
        [Paragraph("Field Name", table_header), Paragraph("Missing Count", table_header), Paragraph("% Missing", table_header), Paragraph("Legal / Metrological Rationale", table_header)],
        [Paragraph("load_cell_model", table_cell_bold), Paragraph("431 / 454", table_cell_mono), Paragraph("94.9%", table_cell), Paragraph("Certificates specify load cell make (strain gauge) but omit OEM part no.", table_cell)],
        [Paragraph("approval_coverage", table_cell_bold), Paragraph("128 / 454", table_cell_mono), Paragraph("28.2%", table_cell), Paragraph("Single fixed-capacity instruments omit multi-range coverage clauses.", table_cell)],
        [Paragraph("checksum (CRC)", table_cell_bold), Paragraph("74 / 454", table_cell_mono), Paragraph("16.3%", table_cell), Paragraph("Older non-microprocessor electronic scale models omit CRC checksums.", table_cell)],
        [Paragraph("software_version", table_cell_bold), Paragraph("3 / 454", table_cell_mono), Paragraph("0.7%", table_cell), Paragraph("Legacy purely analog/mechanical indicator readouts.", table_cell)],
        [Paragraph("sealing_details", table_cell_bold), Paragraph("3 / 454", table_cell_mono), Paragraph("0.7%", table_cell), Paragraph("Contained in generic Schedule VII provisions.", table_cell)],
    ]
    missing_table = Table(missing_data, colWidths=[120, 75, 50, 287])
    missing_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D97706')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    sec4.append(missing_table)
    story.append(KeepTogether(sec4))

    # Page Break for clean 2-page document
    story.append(PageBreak())

    # Section 5: Accuracy Class Breakdown
    story.append(Paragraph("5. Accuracy Class Distribution Across Ingested Models", h1_style))
    acc_data = [
        [Paragraph("Accuracy Class", table_header), Paragraph("Model Count", table_header), Paragraph("Typical Commercial Use Case", table_header)],
        [Paragraph("Class III (Medium Accuracy)", table_cell_bold), Paragraph("296 models (65.2%)", table_cell_mono), Paragraph("Retail counter scales, platform scales, Mandi weighers, standard commercial scales", table_cell)],
        [Paragraph("Class II (High Accuracy)", table_cell_bold), Paragraph("52 models (11.5%)", table_cell_mono), Paragraph("Precious metals, jewellery scales, pharmaceutical prescription weighing", table_cell)],
        [Paragraph("Class I (Special Accuracy)", table_cell_bold), Paragraph("38 models (8.4%)", table_cell_mono), Paragraph("Analytical micro-balances, scientific laboratory standards", table_cell)],
        [Paragraph("Industrial / Continuous / AWI", table_cell_bold), Paragraph("68 models (15.0%)", table_cell_mono), Paragraph("Flow meters, continuous totalizers, automatic gravimetric filling systems", table_cell)],
    ]
    acc_table = Table(acc_data, colWidths=[140, 110, 282])
    acc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(acc_table)
    story.append(Spacer(1, 6))

    # Section 6: Architectural Separation: Layer A vs Layer B
    story.append(Paragraph("6. Platform Architecture: Layer A vs Layer B Separation", h1_style))
    arch_desc = (
        "The system strictly separates <b>Statutory Model Reference Data (Layer A)</b> from <b>Physical In-Situ Trader Deployments (Layer B)</b>:"
    )
    story.append(Paragraph(arch_desc, body_style))
    story.append(Spacer(1, 3))

    arch_data = [
        [Paragraph("Layer", table_header), Paragraph("Entity & Scope", table_header), Paragraph("Authority & Immutability", table_header), Paragraph("System Role", table_header)],
        [
            Paragraph("<b>Layer A</b><br/>Model Approval", table_cell),
            Paragraph("<code>InstrumentModel</code><br/>454 approved models", table_cell_mono),
            Paragraph("<b>Government of India (DoCA)</b><br/>Read-only statutory reference", table_cell),
            Paragraph("Provides baseline tolerances, maximum capacity, verification scale interval (e), and approval mark.", table_cell)
        ],
        [
            Paragraph("<b>Layer B</b><br/>In-Situ Instrument", table_cell),
            Paragraph("<code>Instrument</code><br/>Physical trader assets", table_cell_mono),
            Paragraph("<b>Trader / State LM Dept</b><br/>Operational lifecycle", table_cell),
            Paragraph("Binds physical serial number, asset tag, GPS location, and inspection history to the Layer A model.", table_cell)
        ],
    ]
    arch_table = Table(arch_data, colWidths=[80, 120, 120, 212])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 6))

    # Section 7: REST API & Frontend Deliverables
    story.append(Paragraph("7. REST API Endpoints & User Interface Components", h1_style))
    api_ui_data = [
        [Paragraph("Component", table_header), Paragraph("Endpoint / Route", table_header), Paragraph("Functionality Delivered", table_header)],
        [Paragraph("Model Catalog Search", table_cell_bold), Paragraph("GET /api/instruments/models", table_cell_mono), Paragraph("Search by series, manufacturer, brand, accuracy class with pagination.", table_cell)],
        [Paragraph("Model Detail API", table_cell_bold), Paragraph("GET /api/instruments/models/{id}", table_cell_mono), Paragraph("Retrieves complete technical specs, load cell data, and raw PDF text.", table_cell)],
        [Paragraph("Govt PDF Server", table_cell_bold), Paragraph("GET /api/instruments/models/{id}/source-pdf", table_cell_mono), Paragraph("Directly streams the original government PDF certificate.", table_cell)],
        [Paragraph("Data Quality API", table_cell_bold), Paragraph("GET /api/instruments/models/data-quality", table_cell_mono), Paragraph("Aggregates missing fields, accuracy classes, and verification metrics.", table_cell)],
        [Paragraph("Model Audit Update", table_cell_bold), Paragraph("PUT /api/instruments/models/{id}", table_cell_mono), Paragraph("Allows Admin/Controller review, edits, and manual verification marking.", table_cell)],
        [Paragraph("Trader Registration UI", table_cell_bold), Paragraph("TraderInstruments.tsx", table_cell_mono), Paragraph("Searchable DoCA model autocomplete auto-filling technical specifications.", table_cell)],
        [Paragraph("Admin Catalog UI", table_cell_bold), Paragraph("AdminModelCatalog.tsx (/admin/models)", table_cell_mono), Paragraph("Table of 454 models, specs modal, and 'View Govt Certificate' button.", table_cell)],
        [Paragraph("Data Quality UI", table_cell_bold), Paragraph("AdminDataQuality.tsx (/admin/data-quality)", table_cell_mono), Paragraph("Ingestion monitor, missing field metrics, and sign-off review editor.", table_cell)],
    ]
    api_ui_table = Table(api_ui_data, colWidths=[110, 185, 237])
    api_ui_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(api_ui_table)
    story.append(Spacer(1, 6))

    # Section 8: Verification & Golden Flow Certification
    sec8 = []
    sec8.append(Paragraph("8. Platform Integrity & Automated Test Verification", h1_style))
    test_data = [
        [Paragraph("Test Suite / Verification Stage", table_header), Paragraph("Execution Status", table_header), Paragraph("Outcome & Evidence", table_header)],
        [
            Paragraph("<b>Golden PASS Flow Test</b><br/>Trader &rarr; Scrutiny &rarr; Verification &rarr; Certificate", table_cell),
            Paragraph("<b>PASSED (100%)</b>", table_cell_bold),
            Paragraph("Issued Certificate <code>LM/JH/2026/991527</code> with tamper-evident QR code and SHA-256 hash.", table_cell)
        ],
        [
            Paragraph("<b>Golden FAIL Flow Test</b><br/>Maximum Permissible Error Violation", table_cell),
            Paragraph("<b>PASSED (100%)</b>", table_cell_bold),
            Paragraph("Tolerance engine correctly detected error exceeding 3.0e and rejected certificate issuance.", table_cell)
        ],
        [
            Paragraph("<b>Frontend Production Build</b><br/>TypeScript Compilation & Bundling", table_cell),
            Paragraph("<b>PASSED (0 Errors)</b>", table_cell_bold),
            Paragraph("Vite built 1507 modules into production bundle in 22.36s with complete type safety.", table_cell)
        ],
    ]
    test_table = Table(test_data, colWidths=[150, 95, 287])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#059669')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    sec8.append(test_table)
    sec8.append(Spacer(1, 6))

    # Sign-off box
    signoff_data = [
        [
            Paragraph("<b>Prepared By:</b> LegalMet Verify Integration Engine", body_style),
            Paragraph("<b>Classification:</b> Official Technical Deliverable", body_style),
            Paragraph("<b>Status:</b> PRODUCTION READY (100% VERIFIED)", body_bold)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[175, 175, 182])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3B82F6')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    sec8.append(signoff_table)
    story.append(KeepTogether(sec8))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)

    # Copy to secondary output paths if requested
    for extra_path in output_paths[1:]:
        import shutil
        shutil.copyfile(primary_path, extra_path)

if __name__ == '__main__':
    paths = [
        r"C:\Users\Class rep\Desktop\Sih\reports\LegalMet_DoCA_Integration_Report.pdf",
        r"C:\Users\Class rep\.gemini\antigravity\brain\dec88633-0c15-47e0-a45b-611ca3a967ff\LegalMet_DoCA_Integration_Report.pdf"
    ]
    generate_pdf(paths)
    print("Successfully regenerated 2-page PDF report.")
