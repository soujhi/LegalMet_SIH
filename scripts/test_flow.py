import requests

BASE_URL = "http://127.0.0.1:8000"

def test_golden_flow():
    print("==================================================")
    print("STARTING LEGALMET VERIFY GOLDEN DEMO TEST (PASS)")
    print("==================================================")

    # 1. Login Trader
    trader_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "trader.patel@agrotraders.in",
        "password": "Trader@123"
    }).json()
    t_token = trader_login["access_token"]
    t_headers = {"Authorization": f"Bearer {t_token}"}
    print("[1] Trader Login Successful:", trader_login["user"]["full_name"])

    # Get Trader Instruments
    insts = requests.get(f"{BASE_URL}/api/instruments", headers=t_headers).json()
    target_inst = insts[0]
    print(f"    Selected Instrument: {target_inst['model']['brand']} {target_inst['model']['model_series']} (SN: {target_inst['serial_number']})")

    # Submit Verification Application
    app = requests.post(f"{BASE_URL}/api/applications", headers=t_headers, json={
        "instrument_id": target_inst["id"],
        "application_type": "RE_VERIFICATION"
    }).json()
    app_id = app["id"]
    print(f"[2] Application Submitted: {app['application_number']} | Status: {app['status']}")

    # 2. Login Admin & Scrutinize
    admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@legalmet.gov.in",
        "password": "Admin@123"
    }).json()
    a_token = admin_login["access_token"]
    a_headers = {"Authorization": f"Bearer {a_token}"}
    print("[3] Admin Login Successful:", admin_login["user"]["full_name"])

    # Approve Application
    appv = requests.put(f"{BASE_URL}/api/applications/{app_id}/status", headers=a_headers, json={
        "status": "APPROVED",
        "remarks": "Documents scrutinized and approved for inspection."
    }).json()
    print(f"    Application Approved: Status -> {appv['status']}")

    # Assign LMO Officer & Schedule
    assign = requests.post(f"{BASE_URL}/api/schedule/assign/{app_id}", headers=a_headers, json={
        "officer_id": 1,
        "scheduled_at": "2026-09-28T10:00:00Z",
        "remarks": "Assigned to Inspector Amit Sharma (LMO-JH-001)"
    }).json()
    print(f"[4] Officer Assigned: Status -> {assign['status']}")

    # 3. Login LMO & Field Verification (PASS Flow)
    lmo_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "lmo.sharma@legalmet.gov.in",
        "password": "Lmo@123"
    }).json()
    l_token = lmo_login["access_token"]
    l_headers = {"Authorization": f"Bearer {l_token}"}
    print("[5] LMO Login Successful:", lmo_login["user"]["full_name"])

    # Start Field Verification & Lock GPS
    start = requests.post(f"{BASE_URL}/api/verification/start/{app_id}", headers=l_headers, json={
        "latitude": 24.3015,
        "longitude": 85.4228,
        "location_address": "Barhi Grain Mandi Platform 2"
    }).json()
    print(f"    Field Verification Session Started: GPS ({start['location']['latitude']}, {start['location']['longitude']})")

    # Complete Field Verification with Test Observations (PASS Scenario)
    comp = requests.post(f"{BASE_URL}/api/verification/{app_id}/complete", headers=l_headers, json={
        "observations": [
            {"test_name": "Zero Load Test", "test_type": "ZERO_LOAD", "test_load": 0.0, "expected_value": 0.0, "observed_value": 0.0, "unit": "kg"},
            {"test_name": "Half Capacity Test", "test_type": "HALF_CAPACITY", "test_load": 15.0, "expected_value": 15.0, "observed_value": 15.005, "unit": "kg"},
            {"test_name": "Maximum Capacity Test", "test_type": "MAX_CAPACITY", "test_load": 30.0, "expected_value": 30.0, "observed_value": 30.010, "unit": "kg"},
            {"test_name": "Eccentricity (Corner Load)", "test_type": "ECCENTRICITY", "test_load": 10.0, "expected_value": 10.0, "observed_value": 10.002, "unit": "kg"}
        ],
        "latitude": 24.3015,
        "longitude": 85.4228,
        "location_address": "Barhi Grain Mandi Platform 2",
        "remarks": "All observations pass statutory MPE limits. Stamping wire sealed."
    }).json()
    cert_no = comp["certificate_number"]
    print(f"[6] Verification Complete! Outcome: {comp['overall_result']} | Certificate: {cert_no}")
    print(f"    Generated PDF Path: {comp['pdf_url']}")

    # 4. Public QR Certificate Verification
    pub = requests.get(f"{BASE_URL}/api/public/verify/{cert_no}").json()
    print(f"[7] Public QR Verification: Status -> {pub['status']} | Valid: {pub['is_valid']}")
    print(f"    Issuing Authority: {pub['issuing_authority']}")
    print(f"    SHA-256 Fingerprint: {pub['certificate_hash']}")
    print("==================================================")
    print("GOLDEN DEMO PASS FLOW TEST COMPLETE (100%)")
    print("==================================================")

def test_failure_flow():
    print("\n==================================================")
    print("STARTING FAILURE DEMO TEST (FAIL FLOW)")
    print("==================================================")

    # Login Trader
    trader_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "trader.patel@agrotraders.in",
        "password": "Trader@123"
    }).json()
    t_headers = {"Authorization": f"Bearer {trader_login['access_token']}"}
    inst_id = requests.get(f"{BASE_URL}/api/instruments", headers=t_headers).json()[0]["id"]

    # Submit Application
    app = requests.post(f"{BASE_URL}/api/applications", headers=t_headers, json={
        "instrument_id": inst_id,
        "application_type": "RE_VERIFICATION"
    }).json()
    app_id = app["id"]

    # Admin Approve & Assign
    admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@legalmet.gov.in",
        "password": "Admin@123"
    }).json()
    a_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
    requests.put(f"{BASE_URL}/api/applications/{app_id}/status", headers=a_headers, json={"status": "APPROVED"})
    requests.post(f"{BASE_URL}/api/schedule/assign/{app_id}", headers=a_headers, json={"officer_id": 1, "scheduled_at": "2026-09-28T10:00:00Z"})

    # LMO Complete with FAIL Readings (+0.045 kg error > 0.010 kg MPE)
    lmo_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "lmo.sharma@legalmet.gov.in",
        "password": "Lmo@123"
    }).json()
    l_headers = {"Authorization": f"Bearer {lmo_login['access_token']}"}

    res = requests.post(f"{BASE_URL}/api/verification/{app_id}/complete", headers=l_headers, json={
        "observations": [
            {"test_name": "Zero Load Test", "test_type": "ZERO_LOAD", "test_load": 0.0, "expected_value": 0.0, "observed_value": 0.0, "unit": "kg"},
            {"test_name": "Half Capacity Test", "test_type": "HALF_CAPACITY", "test_load": 15.0, "expected_value": 15.0, "observed_value": 15.045, "unit": "kg"}
        ],
        "remarks": "Observed error exceeds Maximum Permissible Error."
    }).json()

    print(f"[1] Failure Scenario Result: {res['overall_result']}")
    print(f"[2] Certificate Issued: {res['certificate_number']} (Expected: None)")
    print(f"[3] Application Status: {res['status']} (Expected: FAILED)")

    assert res["overall_result"] == "FAIL"
    assert res["certificate_number"] is None
    assert res["status"] == "FAILED"

    print("==================================================")
    print("FAILURE FLOW TEST COMPLETE & VERIFIED (100%)")
    print("==================================================")

if __name__ == "__main__":
    test_golden_flow()
    test_failure_flow()
