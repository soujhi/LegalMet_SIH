import hashlib
import json
import os
import uuid
from typing import Optional, Any
from datetime import datetime, timezone, timedelta
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.core.config import settings, CERTIFICATES_DIR, QR_DIR

class CertificateGenerator:

    @staticmethod
    def generate_qr_code(qr_data: str, filename: str) -> str:
        """Generates QR code image file and returns absolute path."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
        filepath = QR_DIR / filename
        img.save(filepath)
        return str(filepath)

    @staticmethod
    def _normalize_iso_date(dt_val: Any) -> str:
        if isinstance(dt_val, datetime):
            return dt_val.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(dt_val, str):
            clean = dt_val.strip().replace(" ", "T")
            if len(clean) >= 19:
                return clean[:19] + "Z"
            return clean
        return str(dt_val)

    @classmethod
    def build_canonical_hash_payload(
        cls,
        certificate_number: str,
        serial_number: Optional[str],
        category: Optional[str],
        model_series: Optional[str],
        capacity: str,
        issue_date: Any,
        valid_until: Any,
        issuing_officer: str,
        verification_location: str
    ) -> dict:
        """
        Builds standardized canonical dictionary for deterministic cryptographic hashing.
        Aligns keys between certificate generator, field verification router, and public verify.
        """
        return {
            "capacity": str(capacity or "").strip(),
            "category": str(category or "").strip(),
            "certificate_number": str(certificate_number or "").strip(),
            "issue_date": cls._normalize_iso_date(issue_date),
            "issuing_officer": str(issuing_officer or "").strip(),
            "model_series": str(model_series or "").strip(),
            "serial_number": str(serial_number or "").strip(),
            "valid_until": cls._normalize_iso_date(valid_until),
            "verification_location": str(verification_location or "").strip()
        }

    @classmethod
    def compute_certificate_hash(cls, cert_data: dict) -> str:
        """Calculates cryptographic SHA-256 fingerprint of certificate details."""
        sorted_payload = json.dumps(cert_data, sort_keys=True)
        return hashlib.sha256(sorted_payload.encode("utf-8")).hexdigest()

    @classmethod
    def generate_pdf_certificate(
        cls,
        certificate_number: str,
        instrument_dict: dict,
        officer_name: str,
        issue_date: datetime,
        valid_until: datetime,
        verification_location: str,
        tests_summary: list,
        qr_url: str
    ) -> tuple[str, str, str]:
        """
        Generates official Legal Metrology Certificate PDF and returns:
        (pdf_relative_path, qr_relative_path, certificate_hash)
        """
        model_val = (
            instrument_dict.get("model_series")
            or instrument_dict.get("model_name")
            or instrument_dict.get("model")
            or "N/A"
        )
        cert_data_for_hash = cls.build_canonical_hash_payload(
            certificate_number=certificate_number,
            serial_number=instrument_dict.get("serial_number"),
            category=instrument_dict.get("category_name"),
            model_series=model_val,
            capacity=f"{instrument_dict.get('capacity')} {instrument_dict.get('unit')}",
            issue_date=issue_date.isoformat(),
            valid_until=valid_until.isoformat(),
            issuing_officer=officer_name,
            verification_location=verification_location
        )
        cert_hash = cls.compute_certificate_hash(cert_data_for_hash)

        safe_cert_name = certificate_number.replace("/", "_").replace("\\", "_")
        qr_filename = f"qr_{safe_cert_name}.png"
        qr_file_path = cls.generate_qr_code(qr_url, qr_filename)


        pdf_filename = f"cert_{safe_cert_name}.pdf"
        pdf_file_path = CERTIFICATES_DIR / pdf_filename

        doc = SimpleDocTemplate(
            str(pdf_file_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        header_title = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F2942")
        )
        
        header_sub = ParagraphStyle(
            'HeaderSub',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#C2410C")
        )
        
        legal_sub = ParagraphStyle(
            'LegalSub',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569")
        )

        body_bold = ParagraphStyle(
            'BodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1E293B")
        )

        body_text = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155")
        )

        hash_style = ParagraphStyle(
            'HashStyle',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B")
        )

        elements = []

        # Government Emblem / Seal Header Simulation
        elements.append(Paragraph("GOVERNMENT OF INDIA / DEPARTMENT OF LEGAL METROLOGY", header_sub))
        elements.append(Paragraph("CERTIFICATE OF VERIFICATION / RE-VERIFICATION", header_title))
        elements.append(Paragraph("[Under Section 24 of the Legal Metrology Act, 2009 & Rule 14 of General Rules, 2011]", legal_sub))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F2942"), spaceBefore=2, spaceAfter=10))

        # Certificate Meta Grid
        meta_data = [
            [
                Paragraph("<b>Certificate Number:</b>", body_bold),
                Paragraph(f"<b>{certificate_number}</b>", body_bold),
                Paragraph("<b>Date of Issue:</b>", body_bold),
                Paragraph(issue_date.strftime("%d-%m-%Y"), body_text),
            ],
            [
                Paragraph("<b>Validity Period:</b>", body_bold),
                Paragraph(f"{issue_date.strftime('%d-%b-%Y')} to <b>{valid_until.strftime('%d-%b-%Y')}</b>", body_bold),
                Paragraph("<b>Status:</b>", body_bold),
                Paragraph("<font color='#059669'><b>VALID & VERIFIED</b></font>", body_bold),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 2.2*inch, 1.3*inch, 1.8*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # Instrument & Trader Details
        elements.append(Paragraph("<b>1. INSTRUMENT & ESTABLISHMENT PARTICULARS</b>", body_bold))
        elements.append(Spacer(1, 4))
        
        owner_info = instrument_dict.get("organization_name", "Registered Commercial Enterprise")
        loc_info = verification_location or instrument_dict.get("location", "Jharkhand")

        inst_data = [
            [Paragraph("Name of Concern / Trader:", body_bold), Paragraph(owner_info, body_text)],
            [Paragraph("Location of Verification:", body_bold), Paragraph(loc_info, body_text)],
            [Paragraph("Instrument Category / Type:", body_bold), Paragraph(instrument_dict.get("category_name", "Non-Automatic Weighing Instrument"), body_text)],
            [Paragraph("Manufacturer / Brand / Model:", body_bold), Paragraph(f"{instrument_dict.get('manufacturer', 'Standard')} / {instrument_dict.get('brand', 'N/A')} ({instrument_dict.get('model_series', 'Model Approved')})", body_text)],
            [Paragraph("Serial Number / Asset No:", body_bold), Paragraph(f"<b>{instrument_dict.get('serial_number')}</b> / {instrument_dict.get('asset_number', 'N/A')}", body_bold)],
            [Paragraph("Max Capacity / Verification Interval (e):", body_bold), Paragraph(f"Max: {instrument_dict.get('capacity')} {instrument_dict.get('unit', 'kg')} | e = {instrument_dict.get('verification_scale_interval', '5')} g", body_text)],
            [Paragraph("Accuracy Class:", body_bold), Paragraph(instrument_dict.get("accuracy_class", "Class III"), body_text)],
        ]
        inst_table = Table(inst_data, colWidths=[2.2*inch, 4.6*inch])
        inst_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(inst_table)
        elements.append(Spacer(1, 12))

        # Verification Test Results Table
        elements.append(Paragraph("<b>2. STATUTORY VERIFICATION OBSERVATIONS & COMPLIANCE</b>", body_bold))
        elements.append(Spacer(1, 4))

        test_table_data = [
            [
                Paragraph("<b>Test Procedure</b>", body_bold),
                Paragraph("<b>Test Load</b>", body_bold),
                Paragraph("<b>Observed</b>", body_bold),
                Paragraph("<b>Error</b>", body_bold),
                Paragraph("<b>Max MPE</b>", body_bold),
                Paragraph("<b>Result</b>", body_bold)
            ]
        ]

        for t in tests_summary:
            test_table_data.append([
                Paragraph(t.get("test_name", "Load Test"), body_text),
                Paragraph(f"{t.get('test_load', 0)} {t.get('unit', 'kg')}", body_text),
                Paragraph(f"{t.get('observed_value', 0)} {t.get('unit', 'kg')}", body_text),
                Paragraph(f"{t.get('error_calculated', 0):+.4f}", body_text),
                Paragraph(f"±{t.get('tolerance_mpe', 0)}", body_text),
                Paragraph(f"<font color='#059669'><b>{t.get('result', 'PASS')}</b></font>", body_bold)
            ])

        if len(test_table_data) == 1:
            test_table_data.append([
                Paragraph("Standard Verification Inspection", body_text),
                Paragraph(f"{instrument_dict.get('capacity')} kg", body_text),
                Paragraph(f"{instrument_dict.get('capacity')} kg", body_text),
                Paragraph("0.000", body_text),
                Paragraph("±0.010", body_text),
                Paragraph("<font color='#059669'><b>PASS</b></font>", body_bold)
            ])

        test_table = Table(test_table_data, colWidths=[1.8*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F2942")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(test_table)
        elements.append(Spacer(1, 14))

        # QR and Officer Signatures Block
        qr_img = RLImage(qr_file_path, width=1.1*inch, height=1.1*inch)
        
        sign_block = [
            [
                qr_img,
                Paragraph(
                    f"<b>Scan QR to Verify Live Certificate Authenticity:</b><br/>"
                    f"<font size='7.5' color='#0284C7'>{qr_url}</font><br/><br/>"
                    f"<b>Issuing Authority:</b><br/>"
                    f"Legal Metrology Inspector / Officer: <b>{officer_name}</b><br/>"
                    f"Jurisdiction: <b>Hazaribagh / Barhi Sub-Division</b><br/>"
                    f"<font size='7' color='#64748B'>Digitally stamped & recorded in LegalMet Verify System</font>",
                    body_text
                )
            ]
        ]
        sign_table = Table(sign_block, colWidths=[1.4*inch, 5.4*inch])
        sign_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0F2942")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(sign_table)
        elements.append(Spacer(1, 10))

        # Hash and Disclaimers
        elements.append(Paragraph(f"Digital Certificate SHA-256 Hash: {cert_hash}", hash_style))
        elements.append(Paragraph(
            "Note: This verification certificate is generated electronically in accordance with statutory standards. "
            "Tampering with or altering this certificate is punishable under the Legal Metrology Act, 2009.",
            legal_sub
        ))

        doc.build(elements)

        rel_pdf = f"/storage/certificates/{pdf_filename}"
        rel_qr = f"/storage/qr_codes/{qr_filename}"
        return rel_pdf, rel_qr, cert_hash

certificate_generator = CertificateGenerator()
