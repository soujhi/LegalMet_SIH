"""
LegalMet Verify — Statutory Rule Engine, Model Reconciliation & Hash Forensics Unit Matrix
Covers PRD Section 13, 14, 15, 20 & Forensic Audit AMBER Remediation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.rule_engine import rule_engine
from app.services.certificate_generator import certificate_generator
from app.models.models import VerificationResult

def test_rule_engine_matrix():
    print("=" * 60)
    print("RUNNING STATUTORY RULE ENGINE UNIT TEST MATRIX")
    print("=" * 60)

    # Test 1: Class III vs Class IIII precedence (AMBER Item 1)
    # Class IIII input must NOT match Class III
    res_cl4 = rule_engine.evaluate_test(
        accuracy_class="Class IIII",
        capacity=50.0,
        scale_interval_e=20.0, # 20g
        test_load=2.0,         # 2 kg = 100e
        observed_value=2.025,  # error = +0.025 kg
        unit="kg"
    )
    print(f"[1] Class IIII Matching: Rule = {res_cl4['rule_code']} (Class: {res_cl4['accuracy_class']})")
    assert res_cl4["accuracy_class"] == "CLASS IIII", f"Expected CLASS IIII, got {res_cl4['accuracy_class']}"
    assert "CL4" in res_cl4["rule_code"], f"Expected CL4 rule code, got {res_cl4['rule_code']}"

    res_cl3 = rule_engine.evaluate_test(
        accuracy_class="Class III",
        capacity=30.0,
        scale_interval_e=5.0,  # 5g
        test_load=10.0,        # 10 kg = 2000e
        observed_value=10.005,
        unit="kg"
    )
    print(f"[2] Class III Matching: Rule = {res_cl3['rule_code']} (Class: {res_cl3['accuracy_class']})")
    assert res_cl3["accuracy_class"] == "CLASS III"
    assert "CL3" in res_cl3["rule_code"]

    # Test 2: Scale Interval < 1g normalization (AMBER Item 2)
    # Class II high precision scale: e = 0.1g, capacity = 1.0 kg, test load = 0.5 kg
    # m = 0.5 kg / (0.1g / 1000) = 5000e. In-service MPE multiplier = 1.0 -> MPE = 1.0 * 0.0001 kg = 0.0001 kg
    res_cl2_subgram = rule_engine.evaluate_test(
        accuracy_class="Class II",
        capacity=1.0,
        scale_interval_e=0.1,  # 0.1g
        test_load=0.5,         # 0.5 kg
        observed_value=0.50008, # error = +0.00008 kg (<= 0.0001 kg MPE)
        unit="kg",
        scale_interval_unit="g"
    )
    print(f"[3] Sub-gram Scale Interval (e=0.1g): MPE = {res_cl2_subgram['tolerance_mpe']} kg, Error = {res_cl2_subgram['error_calculated']} kg")
    assert abs(res_cl2_subgram["tolerance_mpe"] - 0.0001) < 1e-6, f"Expected 0.0001 MPE, got {res_cl2_subgram['tolerance_mpe']}"
    assert res_cl2_subgram["result"] == VerificationResult.PASS

    # Test 3: Boundary Test - Exactly at MPE
    res_exact_mpe = rule_engine.evaluate_test(
        accuracy_class="Class III",
        capacity=30.0,
        scale_interval_e=5.0,  # 5g -> e = 0.005 kg
        test_load=15.0,        # 15 kg -> m = 3000e -> MPE multiplier = 3.0 -> tolerance_mpe = 0.015 kg
        observed_value=15.015, # error = exactly +0.015 kg
        unit="kg"
    )
    print(f"[4] Boundary Test (Exactly at MPE): Result = {res_cl3['result'].value}")
    assert res_exact_mpe["result"] == VerificationResult.PASS, "Value exactly at MPE should PASS"

    # Test 4: Boundary Test - Slightly Above MPE
    res_above_mpe = rule_engine.evaluate_test(
        accuracy_class="Class III",
        capacity=30.0,
        scale_interval_e=5.0,
        test_load=15.0,
        observed_value=15.016, # error = +0.016 kg > 0.015 kg MPE
        unit="kg"
    )
    print(f"[5] Boundary Test (Above MPE): Result = {res_above_mpe['result'].value}")
    assert res_above_mpe["result"] == VerificationResult.FAIL, "Value above MPE must FAIL"

    # Test 5: Missing regulatory critical inputs -> REVIEW_REQUIRED
    res_missing_class = rule_engine.evaluate_test(
        accuracy_class=None,
        capacity=30.0,
        scale_interval_e=5.0,
        test_load=10.0,
        observed_value=10.0
    )
    print(f"[6] Missing Accuracy Class: Result = {res_missing_class['result'].value} ({res_missing_class['decision']})")
    assert res_missing_class["result"] == VerificationResult.REVIEW_REQUIRED
    assert res_missing_class["decision"] == "REVIEW_REQUIRED"

    res_missing_e = rule_engine.evaluate_test(
        accuracy_class="Class III",
        capacity=30.0,
        scale_interval_e=None,
        test_load=10.0,
        observed_value=10.0
    )
    print(f"[7] Missing Scale Interval e: Result = {res_missing_e['result'].value} ({res_missing_e['decision']})")
    assert res_missing_e["result"] == VerificationResult.REVIEW_REQUIRED

    print("ALL RULE ENGINE TESTS PASSED!\n")

def test_hash_integrity():
    print("=" * 60)
    print("RUNNING CRYPTOGRAPHIC HASH FORENSICS & TAMPER DETECTION TEST")
    print("=" * 60)

    payload = certificate_generator.build_canonical_hash_payload(
        certificate_number="LM/JH/2026/123456",
        serial_number="NK-2026-9901",
        category="Non-Automatic Weighing Instrument",
        model_series="NKTT-30",
        capacity="30.0 kg",
        issue_date="2026-09-27T12:00:00Z",
        valid_until="2027-09-27T12:00:00Z",
        issuing_officer="Amit Sharma",
        verification_location="Barhi Market Yard"
    )
    original_hash = certificate_generator.compute_certificate_hash(payload)
    print(f"[1] Original SHA-256 Fingerprint: {original_hash}")

    # Recomputing exact same payload must yield identical hash
    recomputed_hash = certificate_generator.compute_certificate_hash(payload)
    assert recomputed_hash == original_hash, "Deterministic hash computation failed"
    print("[2] Deterministic Recomputation: PASS (Identical Hash)")

    # Tampering test: modify serial number or capacity
    tampered_payload = dict(payload)
    tampered_payload["capacity"] = "35.0 kg" # Unauthorized modification
    tampered_hash = certificate_generator.compute_certificate_hash(tampered_payload)
    print(f"[3] Tampered SHA-256 Fingerprint: {tampered_hash}")
    assert tampered_hash != original_hash, "Tamper detection failed to detect change!"
    print("[4] Tamper Detection Check: PASS (Cryptographic Hash Mismatch Detected)")

    print("ALL CRYPTOGRAPHIC INTEGRITY TESTS PASSED!\n")

if __name__ == "__main__":
    test_rule_engine_matrix()
    test_hash_integrity()
    print("=" * 60)
    print("ALL UNIT MATRIX AUDIT TESTS PASSED (100%)")
    print("=" * 60)
