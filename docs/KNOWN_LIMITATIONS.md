# Known Limitations & Boundaries

1. **Prototype Boundary:** This platform is a software prototype developed for SIH26036. Physical testing of weighing and measuring instruments remains the statutory responsibility of authorized Legal Metrology officers.
2. **Handwritten Scans OCR Quality:** Historical state certificate scans (such as Jharkhand portal PDFs) frequently contain cursive handwritten entries. Current OCR captures printed templates accurately but exhibits lower confidence on handwritten digits. Therefore, OCR records require mandatory human validation (`manual_verified=True`) before certification.
3. **Public Portal Changes & Anti-Bot Protections:** Public government portals (such as West Bengal e-Parimap or Jharkhand e-Legal Metrology) may update layout structures or introduce CAPTCHA protections. Automated bulk downloaders must respect terms of service and avoid CAPTCHA bypasses.
4. **Model Approval vs Field Inspection:** DoCA Model Approval records represent design and type approvals, not field inspection outcomes. In this architecture, they populate Layer A (the model master catalog) rather than inspection session tables.
5. **Statutory Rules Verification:** All legal tolerance rules in the production table must be verified against the official gazette before being cited as legal authority.
