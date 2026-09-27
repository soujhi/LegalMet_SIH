import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    User, UserRole, Organization, Officer, InstrumentCategory,
    InstrumentModel, Instrument, Application, ApplicationStatus, ApplicationType,
    RegulatoryRule, OCRDocument, SourceProvenance, Certificate, CertificateStatus
)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@legalmet.gov.in").first():
            print("Database already initialized with default seed data.")
            return

        print("Initializing LegalMet Verify Database Schema & Seed Data...")

        # 1. Categories
        nawi = InstrumentCategory(
            code="NAWI",
            name="Non-Automatic Weighing Instrument (NAWI)",
            description="Counter scales, platform scales, digital retail scales, hanging scales, weighbridges",
            standard_rule_ref="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II"
        )
        awi = InstrumentCategory(
            code="AWI",
            name="Automatic Weighing Instrument (AWI)",
            description="Continuous totalizers, automatic gravimetric filling machines, checkweighers",
            standard_rule_ref="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-III"
        )
        capacity_meas = InstrumentCategory(
            code="CAP_MEASURE",
            name="Capacity Measures & Liquid Dispensers",
            description="Fuel dispensing pumps, flow meters, storage tank dipsticks",
            standard_rule_ref="Legal Metrology (General) Rules, 2011 - Eighth Schedule"
        )
        db.add_all([nawi, awi, capacity_meas])
        db.flush()

        # 2. DoCA Approved Models (Layer A - Model Approval Reference Data)
        model1 = InstrumentModel(
            category_id=nawi.id,
            manufacturer="Nilkanth Digital Scale CO.",
            brand="N K SCALE",
            model_series="NKTT",
            accuracy_class="Class III",
            max_capacity=30.0,
            min_capacity=0.100,
            verification_scale_interval=5.0,  # 5g
            capacity_unit="kg",
            display_type="Digital Dual LED Green",
            working_principle="Strain Gauge Load Cell",
            approval_mark="IND/09/2022/145",
            approval_date="14-09-2022",
            source_provenance=SourceProvenance.DOCA_MODEL_APPROVAL
        )
        model2 = InstrumentModel(
            category_id=nawi.id,
            manufacturer="GOONJ Weighing Systems",
            brand="GOONJ",
            model_series="TB-01",
            accuracy_class="Class IIII",
            max_capacity=20.0,
            min_capacity=2.0,
            verification_scale_interval=200.0,  # 200g
            capacity_unit="kg",
            display_type="Mechanical Circular Dial",
            working_principle="Spring Dial Hanging Mechanism",
            approval_mark="IND/09/2021/89",
            approval_date="08-03-2021",
            source_provenance=SourceProvenance.DOCA_MODEL_APPROVAL
        )
        model3 = InstrumentModel(
            category_id=nawi.id,
            manufacturer="Essae-Teraoka Ltd.",
            brand="Essae",
            model_series="DS-215",
            accuracy_class="Class III",
            max_capacity=31.0,
            min_capacity=0.100,
            verification_scale_interval=5.0,
            capacity_unit="kg",
            display_type="LCD Backlit Display",
            working_principle="High Precision Strain Gauge",
            approval_mark="IND/09/2020/601",
            approval_date="22-11-2020",
            source_provenance=SourceProvenance.DOCA_MODEL_APPROVAL
        )
        db.add_all([model1, model2, model3])
        db.flush()

        # 3. Regulatory Rules (Deterministic Statutory Reference Rules)
        rule1 = RegulatoryRule(
            rule_code="LM-NAWI-CL3-R1",
            category_id=nawi.id,
            accuracy_class="Class III",
            test_type="LOAD_TEST",
            min_range_e=0.0,
            max_range_e=500.0,
            mpe_formula="±1.0 e (In-Service / Re-verification)",
            mpe_multiplier=1.0,
            is_verified_government_rule=True,
            rule_source_reference="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1",
            description="For Class III instruments up to 500e load (e.g. 0 to 2.5 kg for e=5g), Maximum Permissible Error is ±1.0e."
        )
        rule2 = RegulatoryRule(
            rule_code="LM-NAWI-CL3-R2",
            category_id=nawi.id,
            accuracy_class="Class III",
            test_type="LOAD_TEST",
            min_range_e=500.0,
            max_range_e=2000.0,
            mpe_formula="±2.0 e (In-Service / Re-verification)",
            mpe_multiplier=2.0,
            is_verified_government_rule=True,
            rule_source_reference="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1",
            description="For Class III instruments from 500e to 2000e load (e.g. 2.5 kg to 10 kg for e=5g), Maximum Permissible Error is ±2.0e."
        )
        rule3 = RegulatoryRule(
            rule_code="LM-NAWI-CL3-R3",
            category_id=nawi.id,
            accuracy_class="Class III",
            test_type="LOAD_TEST",
            min_range_e=2000.0,
            max_range_e=10000.0,
            mpe_formula="±3.0 e (In-Service / Re-verification)",
            mpe_multiplier=3.0,
            is_verified_government_rule=True,
            rule_source_reference="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1",
            description="For Class III instruments exceeding 2000e load (e.g. 10 kg to 30 kg for e=5g), Maximum Permissible Error is ±3.0e."
        )
        rule4 = RegulatoryRule(
            rule_code="LM-NAWI-CL4-R1",
            category_id=nawi.id,
            accuracy_class="Class IIII",
            test_type="LOAD_TEST",
            min_range_e=0.0,
            max_range_e=50.0,
            mpe_formula="±1.0 e",
            mpe_multiplier=1.0,
            is_verified_government_rule=True,
            rule_source_reference="Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 2",
            description="Class IIII ordinary accuracy scales up to 50e."
        )
        db.add_all([rule1, rule2, rule3, rule4])

        # 4. Organizations
        org_trader1 = Organization(
            name="Patel Agro Commodities & Seeds",
            trade_name="Patel Agro Barhi",
            registration_number="JH-HAZ-2023-9941",
            address="Shop No 14, Main Mandi Road, Barhi",
            state="Jharkhand",
            district="Hazaribagh",
            pincode="825405",
            contact_email="trader.patel@agrotraders.in",
            contact_phone="+91 98351 22345"
        )
        org_trader2 = Organization(
            name="Gupta Kirana & General Store",
            trade_name="Gupta Provisions",
            registration_number="JH-HAZ-2022-1104",
            address="Station Chowk, Barhi",
            state="Jharkhand",
            district="Hazaribagh",
            pincode="825405",
            contact_email="trader.gupta@barhistore.in",
            contact_phone="+91 94311 88762"
        )
        db.add_all([org_trader1, org_trader2])
        db.flush()

        # 5. Users
        admin_user = User(
            email="admin@legalmet.gov.in",
            hashed_password=get_password_hash("Admin@123"),
            full_name="Rajesh Verma (Senior Inspector / Admin)",
            role=UserRole.ADMIN,
            phone="+91 94311 00001",
            is_active=True
        )
        lmo_user = User(
            email="lmo.sharma@legalmet.gov.in",
            hashed_password=get_password_hash("Lmo@123"),
            full_name="Amit Sharma",
            role=UserRole.LMO,
            phone="+91 94311 23456",
            is_active=True
        )
        trader_user1 = User(
            email="trader.patel@agrotraders.in",
            hashed_password=get_password_hash("Trader@123"),
            full_name="Ramesh Patel",
            role=UserRole.TRADER,
            phone="+91 98351 22345",
            organization_id=org_trader1.id,
            is_active=True
        )
        trader_user2 = User(
            email="trader.gupta@barhistore.in",
            hashed_password=get_password_hash("Trader@123"),
            full_name="Sanjay Gupta",
            role=UserRole.TRADER,
            phone="+91 94311 88762",
            organization_id=org_trader2.id,
            is_active=True
        )
        db.add_all([admin_user, lmo_user, trader_user1, trader_user2])
        db.flush()

        # 6. Officer Profile
        officer = Officer(
            user_id=lmo_user.id,
            officer_code="LMO-JH-001",
            designation="Legal Metrology Inspector (LMO)",
            jurisdiction_state="Jharkhand",
            jurisdiction_district="Barhi / Hazaribagh",
            badge_number="JH-LM-9921"
        )
        db.add(officer)
        db.flush()

        # 7. Demo Instruments
        inst1 = Instrument(
            organization_id=org_trader1.id,
            category_id=nawi.id,
            model_id=model1.id,
            serial_number="NK-2024-8841",
            asset_number="MANDI-SCALE-01",
            capacity=30.0,
            unit="kg",
            accuracy_class="Class III",
            verification_scale_interval=5.0,  # 5g
            location="Barhi Grain Mandi Platform 2",
            status="ACTIVE",
            source_provenance=SourceProvenance.DEMO_DATA
        )
        inst2 = Instrument(
            organization_id=org_trader2.id,
            category_id=nawi.id,
            model_id=model2.id,
            serial_number="GJ-99120",
            asset_number="STORE-SCALE-02",
            capacity=20.0,
            unit="kg",
            accuracy_class="Class IIII",
            verification_scale_interval=200.0,
            location="Gupta General Store Counter",
            status="ACTIVE",
            source_provenance=SourceProvenance.DEMO_DATA
        )
        db.add_all([inst1, inst2])
        db.flush()

        # 8. Import Jharkhand Government OCR Data (Layer B - State Field Records)
        json_path = Path(__file__).resolve().parent.parent.parent / "data" / "government" / "jharkhand" / "jharkhand_barhi_certificates.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for item in records[:30]:  # Seed initial batch of Jharkhand government records
                    ocr_rec = OCRDocument(
                        source_file=f"jharkhand_{item.get('certificate_no', 'cert')}.pdf",
                        certificate_no=item.get("certificate_no"),
                        area=item.get("area", "BARHI"),
                        concern_name=item.get("concern_name"),
                        verification_date="01/04/2024",
                        next_verification_date="31/03/2025",
                        instrument_type="Non-Automatic Weighing Instrument",
                        manufacturer="Nilkanth Digital Scale CO. / Standard",
                        model="Commercial Counter Scale",
                        capacity="30 kg",
                        accuracy_class="Class III",
                        verification_fee="Rs. 250/-",
                        raw_ocr_text=f"JHARKHAND LEGAL METROLOGY CERTIFICATE #{item.get('certificate_no')} for {item.get('concern_name')} at {item.get('area')}.",
                        ocr_confidence=88.5,
                        manual_verified=False,
                        source_type=SourceProvenance.GOVERNMENT_PORTAL
                    )
                    db.add(ocr_rec)

        db.commit()
        print("Database initialization complete with sample data, rules, DoCA models and Jharkhand records!")

    except Exception as e:
        db.rollback()
        print(f"Error during db init: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
