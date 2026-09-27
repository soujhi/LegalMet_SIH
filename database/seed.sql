-- LegalMet Verify (SIH26036) Seed Data SQL

-- 1. Categories
INSERT INTO instrument_categories (id, code, name, description, standard_rule_ref) VALUES
(1, 'NAWI', 'Non-Automatic Weighing Instrument (NAWI)', 'Counter scales, platform scales, digital retail scales, hanging scales', 'Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II'),
(2, 'AWI', 'Automatic Weighing Instrument (AWI)', 'Continuous totalizers, automatic gravimetric filling machines, checkweighers', 'Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-III'),
(3, 'CAP_MEASURE', 'Capacity Measures & Liquid Dispensers', 'Fuel dispensing pumps, flow meters, storage tank dipsticks', 'Legal Metrology (General) Rules, 2011 - Eighth Schedule');

-- 2. DoCA Approved Models (Layer A)
INSERT INTO instrument_models (id, category_id, manufacturer, brand, model_series, accuracy_class, max_capacity, min_capacity, verification_scale_interval, capacity_unit, display_type, working_principle, approval_mark, approval_date, source_provenance) VALUES
(1, 1, 'Nilkanth Digital Scale CO.', 'N K SCALE', 'NKTT', 'Class III', 30.0, 0.100, 5.0, 'kg', 'Digital Dual LED Green', 'Strain Gauge Load Cell', 'IND/09/2022/145', '14-09-2022', 'DOCA_MODEL_APPROVAL'),
(2, 1, 'GOONJ Weighing Systems', 'GOONJ', 'TB-01', 'Class IIII', 20.0, 2.0, 200.0, 'kg', 'Mechanical Circular Dial', 'Spring Dial Hanging Mechanism', 'IND/09/2021/89', '08-03-2021', 'DOCA_MODEL_APPROVAL'),
(3, 1, 'Essae-Teraoka Ltd.', 'Essae', 'DS-215', 'Class III', 31.0, 0.100, 5.0, 'kg', 'LCD Backlit Display', 'High Precision Strain Gauge', 'IND/09/2020/601', '22-11-2020', 'DOCA_MODEL_APPROVAL');

-- 3. Statutory Rules
INSERT INTO regulatory_rules (id, rule_code, category_id, accuracy_class, test_type, min_range_e, max_range_e, mpe_formula, mpe_multiplier, is_verified_government_rule, rule_source_reference, description) VALUES
(1, 'LM-NAWI-CL3-R1', 1, 'Class III', 'LOAD_TEST', 0.0, 500.0, '±1.0 e (In-Service / Re-verification)', 1.0, 1, 'Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1', 'Class III loads up to 500e (MPE ±1.0e).'),
(2, 'LM-NAWI-CL3-R2', 1, 'Class III', 'LOAD_TEST', 500.0, 2000.0, '±2.0 e (In-Service / Re-verification)', 2.0, 1, 'Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1', 'Class III loads from 500e to 2000e (MPE ±2.0e).'),
(3, 'LM-NAWI-CL3-R3', 1, 'Class III', 'LOAD_TEST', 2000.0, 10000.0, '±3.0 e (In-Service / Re-verification)', 3.0, 1, 'Legal Metrology (General) Rules, 2011 - Seventh Schedule, Part-II, Table 1', 'Class III loads exceeding 2000e (MPE ±3.0e).');
