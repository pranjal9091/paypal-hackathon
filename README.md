# Outcome Exchange

> **PayPal AI Hackathon 2026** — Buyer-Governed Multi-Agent AI Fulfillment with PayPal Authorization Hold & Deterministic Verification.

---

## What is Outcome Exchange?

In autonomous AI commerce, agents should not have unilateral authority to spend money or settle their own invoices. 

**Outcome Exchange** is an outcome-based fulfillment system where:
1. A **Buyer Agent** structures an outcome agreement with explicit, non-subjective acceptance tests.
2. The buyer places a real **PayPal Sandbox Authorization Hold** (`intent: "AUTHORIZE"`). Funds are held securely on PayPal rails—**not captured**.
3. Specialized worker agents (Localization Agent, Content Agent, QA Agent) execute bounded tasks producing real digital deliverables.
4. An **Automated Deterministic Verifier** validates deliverables against contract criteria (JSON syntax, 100% key parity, variable placeholder retention like `{email}`).
5. An **Authoritative Backend Gate** requires both complete verification pass AND explicit human buyer sign-off before executing `POST /v2/payments/authorizations/{id}/capture`. If deliverables fail or an attack is detected, the hold is voided at zero cost.

---

## Milestone 1: Functional Vertical Slice

Milestone 1 implements the complete end-to-end core lifecycle:
* **Contract**: Spanish Launch Kit for fictional startup *TidyLedger* ($40.00 USD).
* **Payment Rail**: PayPal REST API v2 Order Authorization Hold (`intent: "AUTHORIZE"`), Capture, and Void.
* **Agent**: Spanish Localization Agent generating `es_translations.json`.
* **Verifier**: Deterministic Verifier validating JSON syntax, required key set, non-empty values, and placeholder `{email}` / `{user}` / `{count}` preservation.
* **Backend Security Gate**: Validates verification findings, amount immutability, state prerequisites, and idempotency to block duplicate or unauthorized captures.
* **Audit Trail**: Full event log linking contract intent, deliverables, verification findings, PayPal authorization ID, and PayPal capture ID into an immutable receipt.

---

## Local Setup & Quickstart

### Prerequisites
* Python 3.12+ installed
* Node.js v20+ (for future frontend modules)
* Git

### 1. Setup Backend Virtual Environment
```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
To use live PayPal Sandbox credentials, set:
```env
PAYPAL_ENV=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
```
*Note: If credentials are not supplied, the backend automatically operates in labeled Sandbox Mock Mode (`is_mock: true`), providing offline test and judging reliability.*

### 3. Launch Application
```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate in your browser to:
* **Interactive Vertical Slice Dashboard**: `http://localhost:8000/`
* **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`

---

## Running the Automated Test Suite

Run the 13 automated tests covering all 6 mandatory hackathon security scenarios:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

### Verified Test Scenarios
1. `test_verifier_passes_on_valid_deliverable`: Verifies complete JSON, matching keys, and preserved placeholders.
2. `test_verifier_fails_on_missing_key`: Confirms missing deliverable keys are flagged.
3. `test_verifier_fails_on_corrupted_placeholder`: Flags missing `{email}` or `{user}` tokens.
4. `test_verifier_fails_on_empty_translation`: Catches blank string translations.
5. `test_verifier_fails_on_invalid_json_syntax`: Catches malformed JSON.
6. `test_successful_end_to_end_vertical_slice`: Complete workflow from creation to capture receipt.
7. `test_missing_deliverable_blocks_capture`: Missing deliverable or failed check prevents payment capture.
8. `test_capture_without_buyer_approval_rejected`: Capturing with `buyer_approved=False` returns HTTP 400.
9. `test_modified_amount_rejected`: Captured amount is strictly read from database record, ignoring client tampering.
10. `test_duplicate_capture_handled_safely`: Repeated capture attempts return HTTP 409 Conflict.
11. `test_prompt_injection_input_untrusted`: Prompt injection in input files remains untrusted string data and cannot override payment status.
12. `test_illegal_state_transition_from_draft`: Prevents illegal contract state transitions.
13. `test_transition_to_awaiting_approval_requires_all_findings_passed`: Enforces state machine invariants.

---

## License

Apache License 2.0.
