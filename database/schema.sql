-- LegalMet Verify (SIH26036) Database Schema
-- Compatible with PostgreSQL and SQLite

CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    registration_number VARCHAR(100) UNIQUE,
    address TEXT,
    state VARCHAR(100) NOT NULL DEFAULT 'Jharkhand',
    district VARCHAR(100),
    pincode VARCHAR(20),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- TRADER, ADMIN, LMO, PUBLIC
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    organization_id INTEGER REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    officer_code VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(150) DEFAULT 'Legal Metrology Officer (LMO)',
    jurisdiction_state VARCHAR(100) DEFAULT 'Jharkhand',
    jurisdiction_district VARCHAR(100) DEFAULT 'Hazaribagh / Barhi',
    badge_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS instrument_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    standard_rule_ref VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS instrument_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES instrument_categories(id),
    manufacturer VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    model_series VARCHAR(255) NOT NULL,
    accuracy_class VARCHAR(50) NOT NULL,
    max_capacity REAL NOT NULL,
    min_capacity REAL NOT NULL,
    verification_scale_interval REAL NOT NULL,
    capacity_unit VARCHAR(20) DEFAULT 'kg',
    display_type VARCHAR(50) DEFAULT 'Digital LED/LCD',
    working_principle VARCHAR(100) DEFAULT 'Strain Gauge Load Cell',
    approval_mark VARCHAR(100),
    approval_date VARCHAR(50),
    source_provenance VARCHAR(50) DEFAULT 'DOCA_MODEL_APPROVAL'
);

CREATE TABLE IF NOT EXISTS instruments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    category_id INTEGER NOT NULL REFERENCES instrument_categories(id),
    model_id INTEGER REFERENCES instrument_models(id),
    serial_number VARCHAR(100) NOT NULL,
    asset_number VARCHAR(100),
    capacity REAL NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    accuracy_class VARCHAR(50) DEFAULT 'Class III',
    verification_scale_interval REAL DEFAULT 5.0,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    last_verified_date TIMESTAMP,
    next_verification_date TIMESTAMP,
    source_provenance VARCHAR(50) DEFAULT 'DEMO_DATA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_number VARCHAR(100) UNIQUE NOT NULL,
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    applicant_id INTEGER NOT NULL REFERENCES users(id),
    organization_id INTEGER REFERENCES organizations(id),
    application_type VARCHAR(50) DEFAULT 'RE_VERIFICATION',
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewer_id INTEGER REFERENCES users(id),
    reviewer_notes TEXT,
    scheduled_at TIMESTAMP,
    assigned_officer_id INTEGER REFERENCES officers(id),
    payment_status VARCHAR(50) DEFAULT 'PAID',
    payment_amount REAL DEFAULT 250.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS application_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL REFERENCES applications(id),
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    remarks TEXT,
    changed_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER UNIQUE NOT NULL REFERENCES applications(id),
    officer_id INTEGER NOT NULL REFERENCES officers(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    latitude REAL,
    longitude REAL,
    location_accuracy REAL,
    location_address VARCHAR(500),
    device_timestamp TIMESTAMP,
    overall_result VARCHAR(50) DEFAULT 'IN_PROGRESS',
    remarks TEXT,
    photos_json JSON,
    signature_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES verification_sessions(id),
    test_name VARCHAR(150) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    test_load REAL NOT NULL,
    expected_value REAL NOT NULL,
    observed_value REAL NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    tolerance_mpe REAL NOT NULL,
    error_calculated REAL NOT NULL,
    result VARCHAR(50) NOT NULL,
    rule_applied_id INTEGER,
    remarks TEXT
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    certificate_number VARCHAR(100) UNIQUE NOT NULL,
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    application_id INTEGER UNIQUE NOT NULL REFERENCES applications(id),
    verification_session_id INTEGER UNIQUE NOT NULL REFERENCES verification_sessions(id),
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'VALID',
    pdf_url VARCHAR(500),
    qr_token VARCHAR(255) UNIQUE NOT NULL,
    certificate_hash VARCHAR(128) NOT NULL,
    issuing_officer_id INTEGER NOT NULL REFERENCES officers(id),
    issuing_officer_name VARCHAR(255) NOT NULL,
    verification_location VARCHAR(255),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regulatory_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code VARCHAR(100) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL REFERENCES instrument_categories(id),
    accuracy_class VARCHAR(50) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    min_range_e REAL NOT NULL,
    max_range_e REAL NOT NULL,
    mpe_formula VARCHAR(100) NOT NULL,
    mpe_multiplier REAL NOT NULL,
    is_verified_government_rule BOOLEAN DEFAULT TRUE,
    rule_source_reference VARCHAR(500) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS ocr_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file VARCHAR(255) NOT NULL,
    certificate_no VARCHAR(100),
    area VARCHAR(100) DEFAULT 'BARHI',
    concern_name VARCHAR(255),
    verification_date VARCHAR(50),
    next_verification_date VARCHAR(50),
    instrument_type VARCHAR(255),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    capacity VARCHAR(100),
    accuracy_class VARCHAR(50),
    verification_fee VARCHAR(50),
    raw_ocr_text TEXT,
    ocr_confidence REAL DEFAULT 0.0,
    manual_verified BOOLEAN DEFAULT FALSE,
    verified_by_id INTEGER REFERENCES users(id),
    source_type VARCHAR(50) DEFAULT 'GOVERNMENT_PORTAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
