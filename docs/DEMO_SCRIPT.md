# Golden Demo & Failure Demo Script

## 1. Demo Credentials
- **Trader Account:** `trader.patel@agrotraders.in` | Password: `Trader@123` (or click **Trader** in navbar Demo Switcher)
- **Admin Account:** `admin@legalmet.gov.in` | Password: `Admin@123` (or click **Admin** in navbar Demo Switcher)
- **LMO Inspector Account:** `lmo.sharma@legalmet.gov.in` | Password: `Lmo@123` (or click **LMO Officer** in navbar Demo Switcher)

---

## 2. Golden Demo Walkthrough (PASS Flow)

### Step 1: Trader Registers Instrument & Files Verification
1. Click **Trader** in top-right Demo Switcher.
2. Go to **My Instruments** (`/trader/instruments`). View registered `NK SCALE NKTT 30kg` (Serial: `NK-2024-8841`).
3. Click **Applications** (`/trader/applications`) → Click **Apply for Verification**.
4. Select `NK SCALE (NK-2024-8841)`, choose `Periodic Re-Verification`, and click **Submit Application**.
5. Application status immediately displays `SUBMITTED`.

### Step 2: Admin Scrutiny & Officer Assignment
1. Switch to **Admin** via top navbar.
2. Go to **Scrutiny & Schedule** (`/admin/applications`).
3. Locate the new `SUBMITTED` application. Click **Approve**.
4. Status changes to `APPROVED`. Click **Assign LMO**.
5. Select `Amit Sharma (LMO-JH-001)`, pick appointment time, and click **Confirm Action**.
6. Status transitions to `ASSIGNED`.

### Step 3: LMO Mobile Field Verification & Rule Engine
1. Switch to **LMO Officer** via top navbar.
2. Open **Field Inspections** (`/lmo/dashboard`). See the assigned inspection for `Patel Agro Commodities`.
3. Click **Start Field Verification**.
4. Click **Lock Current GPS** to record coordinates (`24.3015° N, 85.4228° E`) and device timestamp.
5. Click **Preset PASS** button (Zero load 0kg, Half load 15kg observed 15.005kg, Max load 30kg observed 30.010kg).
6. Click **Evaluate & Submit Verification Result**.
7. Deterministic Rule Engine evaluates: Error $\le$ MPE ($\pm 0.010\,\text{kg}$).
8. Status transitions to `PASSED` $\rightarrow$ `CERTIFICATE_ISSUED`.
9. Generated Certificate Number displays (e.g. `LM/JH/2026/XXXXXX`) with download PDF button.

### Step 4: Public QR Certificate Verification
1. Click **Test Public QR Verification** or open `/verify/{certificate_number}`.
2. Verification page immediately displays `CERTIFICATE VALID & VERIFIED` with official seal, SHA-256 hash, validity period, issuing officer, and compliance table.

---

## 3. Failure Demo Walkthrough (FAIL Flow)
1. In LMO inspection screen, click **Preset FAIL** button (Observed error exceeds $+0.045\,\text{kg} > \text{MPE } \pm 0.010\,\text{kg}$).
2. Click **Evaluate & Submit Verification Result**.
3. Deterministic Rule Engine outputs: `FAIL — Error Exceeds Statutory MPE`.
4. Status transitions to `FAILED`.
5. System **prevents certificate generation** and automatically logs a `HIGH` severity Risk Flag in the audit repository.
