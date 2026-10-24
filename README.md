# Outcome Exchange

> **PayPal AI Hackathon 2026 Submission**  
> **Buyer-Governed Multi-Agent AI Fulfillment with Official PayPal Sandbox Authorization Hold & Independent Deterministic Verification**

---

## 1. Problem Solved & Core Value Proposition

In autonomous AI commerce, agents should never have unilateral authority to spend money or settle their own invoices. 

* **The Problem:** Current agentic systems either lack real financial rails (relying on mock tokens) or grant LLMs unrestricted API access to debit cards and bank accounts. When an agent hallucinates, drops deliverables, or claims work is finished without proof, buyer funds are drained with zero recourse.
* **The Solution:** **Outcome Exchange** introduces a **Buyer-Governed Architecture** that couples official PayPal payment rails with independent, deterministic deliverable verification and two non-negotiable human gates:
  1. **Pre-Commitment Hold (Not Escrow):** PayPal Orders v2 with `intent: "AUTHORIZE"` places a temporary hold on the approved budget. Funds remain on PayPal rails and are **never captured prematurely**.
  2. **Multi-Agent Fulfillment:** Specialized worker agents (Localization Agent, Content Agent, QA Agent) execute bounded tasks producing concrete digital assets (`es_translations.json`, `landing_page_es.md`, `qa_report.json`).
  3. **Deterministic Deliverable Verification:** Non-subjective verification rules validate syntax, required-key parity, interpolation token preservation (`{email}`, `{user}`), document structure, word-count limits, and regulatory claim safety.
  4. **Informational QA Review:** A QA Agent evaluates cross-artifact tone and terminology. Its findings are recorded informatively and **cannot bypass or weaken deterministic gates**.
  5. **Authoritative Human-Controlled Release Gate:** The server strictly prevents capture unless 100% of mandatory checks pass AND the human buyer explicitly authorizes the release.
  6. **Clean Void/Refund:** If deliverables fail verification, the buyer can void the authorization hold at **$0 charge**.

```
                   OUTCOME EXCHANGE ARCHITECTURE & DATA FLOW

  [ Buyer (Human) ]
         │ (1) Natural Language Goal: "Spanish Launch Kit, Budget: $40"
         ▼
  [ Buyer Agent ] ─── extracts ───► Deliverables, Criteria & Budget ($40.00)
         │
  [ Human Gate 1 ] ─── explicit sign-off ───► Authoritative Contract (DRAFT)
         │
  [ PayPal Agent Toolkit (MCP) ] ─── POST /v2/checkout/orders (intent=AUTHORIZE)
         │
  [ PayPal Rails ] ◄─── Authorization Hold ($40.00 Held, $0 Captured)
         │
         ├───► [ Localization Agent ] ───► es_translations.json
         ├───► [ Content Agent ]      ───► landing_page_es.md
         └───► [ QA Agent ]           ───► qa_report.json
                         │
  [ Independent Deterministic Verifier ]
         │ Checks: Syntax, Parity, Placeholders, Markdown Sections, Claims
         ├───────────────────────────────┐
         ▼ (Fail)                        ▼ (Pass)
  [ Capture Blocked ]             [ Payment Gate Unlocked ]
  (Hold voided at $0)                    │
                                  [ Human Gate 2 ] ─── explicit buyer sign-off
                                         │
                                  [ PayPal Capture Engine ]
                                  POST /v2/payments/authorizations/{id}/capture
                                         │
                                  [ Settled Receipt & Immutable Audit Trail ]
```

---

## 2. Milestone 4 Enhancements & System Audit

Milestone 4 elevates Outcome Exchange to a judge-ready, fully validated submission:

| Area | Milestone 3 Baseline | Milestone 4 Enhancement | Status |
| :--- | :--- | :--- | :--- |
| **PayPal Sandbox Integration** | Mock/Adapter foundation | Full PayPal Orders v2 & Payments v2 integration with `application_context`, `return_url`, `cancel_url`, `PayPal-Request-Id` idempotency, and representation preference. | **Verified / Hardened** |
| **Payment Safety Gates** | Server checks | Order ID validation against contract record, strict rejection of forged/tampered authorization IDs, atomic duplicate capture prevention (HTTP 409). | **47 Passing Tests** |
| **AI Integration & Fallback** | Local fallback engine | Dual-mode: Live Gemini / OpenAI REST integration with strict schema parsing, markdown fence stripping, and bounded retries; transparent labeled fallback. | **Live / Fallback Auditable** |
| **UX & Product Design** | Functional prototype | Premium, restrained fintech interface: 6-step progress indicator, honest environment badges, deliverable viewer, and checklist pass/fail report. | **Production-Grade** |
| **Demo Mode That Never Lies** | Basic test script | One-click reproducible scenarios: Happy Path, Deliverable Failure & Recovery, Adversarial Prompt Injection Containment. | **Judge-Ready** |

---

## 3. Local Setup & Quickstart

### Prerequisites
* Python 3.12+
* Git
* Modern web browser

### Step 1: Clone and Set Up Virtual Environment
```bash
git clone https://github.com/pranjalsingh/paypal-hackathon.git
cd paypal-hackathon
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 2: Environment Configuration
Copy the configuration template:
```bash
cp .env.example .env
```
Inspect or edit `.env`:
```env
# PayPal Sandbox Settings (Defaults to transparent Sandbox Mock if omitted)
PAYPAL_ENV=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret_here

# AI Provider Settings (Defaults to deterministic fallback if omitted)
LLM_PROVIDER=gemini       # Options: gemini, openai, mock
LLM_API_KEY=your_api_key  # Server-side only; never printed or committed
LLM_MODEL=gemini-2.5-flash
LLM_TIMEOUT_SECONDS=15.0

# Server Binding
API_HOST=127.0.0.1
API_PORT=8000
DATABASE_URL=sqlite:///./outcome_exchange.db
```

> **Security & Transparency Policy:**
> If PayPal credentials or LLM keys are absent, the application runs seamlessly using its **Mock Sandbox Engine** (`is_mock=True`) and **Deterministic Fallback Engine** (`is_fallback=True`). The UI and API explicitly label all mock operations. **No simulated transaction is ever misrepresented as a live transaction.**

### Step 3: Run the Application
```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open in browser:
* **Interactive Fintech Application:** `http://127.0.0.1:8000/`
* **Swagger API Specification:** `http://127.0.0.1:8000/docs`

---

## 4. Automated Test Suite (47 Passing Tests)

Run the full automated test suite:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

### Test Suite Summary
* **`test_milestone4_security_regression.py` (11 tests):**
  - `test_forged_order_identifier_rejected`: Confirms invalid/forged order IDs are blocked with HTTP 400.
  - `test_forged_authorization_identifier_rejected`: Confirms forged authorization IDs cannot trigger settlement.
  - `test_failed_verification_cannot_be_overwritten`: Proves client cannot bypass verification findings.
  - `test_duplicate_capture_replayed_request_rejected`: Verifies HTTP 409 Conflict on repeated capture attempts.
  - `test_contract_amount_tampering_strictly_ignored`: Confirms amount sent in capture request is ignored in favor of contract record.
  - `test_absent_paypal_credentials_never_claims_live_success`: Ensures honest mock labeling when keys are absent.
  - `test_mcp_caller_cannot_capture_funds`: Verifies capture is strictly omitted from agent tool definitions.
  - `test_malformed_model_output_falls_back_safely`: Verifies invalid LLM output triggers structured fallback.
  - `test_audit_history_persists_across_queries`: Validates audit log persistence across page refreshes.
  - `test_prompt_injection_payment_request_contained`: Verifies prompt injection cannot override budget.
  - `test_missing_deliverable_blocks_capture_at_route_level`: Route-level proof that 0 deliverables blocks capture.
* **`test_buyer_agent_and_mcp.py` (12 tests):** Natural language parsing, clarification dialogues, MCP tool schema execution, and correlation ID tracing.
* **`test_deterministic_verifier.py` (5 tests):** Syntax validation, missing keys, corrupted interpolation tokens (`{email}`), empty strings.
* **`test_multi_agent_execution.py` (11 tests):** Bundle generation, missing sections, word-count violations, unsupported claims, and QA agent review containment.
* **`test_vertical_slice_security.py` (6 tests):** End-to-end authorization hold, deterministic verifier gate, and human sign-off.
* **`test_state_machine.py` (2 tests):** Illegal transition rejection and prerequisite invariant enforcement.

---

## 5. 3-Minute Hackathon Demo Script

Designed for a live judge presentation or recorded demo under 3 minutes:

| Time | Step | Action | Key Talking Point for Judges |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:30** | **Hook** | Open `http://127.0.0.1:8000/`. Point out the **System Status Bar**. | *"In agentic AI, agents shouldn't be allowed to spend money just because they claim work is done. Outcome Exchange is buyer-governed: real PayPal holds, deterministic verification, and human release gates."* |
| **0:30 - 1:00** | **Formulation & Hold** | Click **Scenario A: Happy Path** (or manually input prompt & confirm). | *"The Buyer Agent parses the request into a contract with acceptance criteria rationale. At Gate 1, the buyer confirms terms, placing an official PayPal Orders v2 authorization hold for $40.00. Funds are held on PayPal rails—not escrow, but delayed capture."* |
| **1:00 - 1:40** | **Multi-Agent Fulfillment** | View the 3 specialist agents generating `es_translations.json`, `landing_page_es.md`, and `qa_report.json`. | *"Specialist agents generate concrete files. Notice the deliverable tabs. The QA Agent provides qualitative review, but cannot override deterministic checks."* |
| **1:40 - 2:20** | **Verification & Failure Gate** | Click **Scenario B: Deliverable Failure & Recovery**. | *"Watch what happens if an agent omits a required section: Verification immediately fails. The payment release gate is strictly LOCKED. No money can move. We recover by re-running the agents, and the gate unlocks."* |
| **2:20 - 2:45** | **Human Gate & Capture** | Check the buyer authorization checkbox and click **Approve Deliverables & Capture $40.00**. | *"Even with 100% verification pass, capture requires explicit buyer sign-off (Gate 2). The backend executes delayed capture and records the PayPal Capture ID."* |
| **2:45 - 3:00** | **Settlement & Audit** | Scroll to **Step 6: Official Transaction Receipt & Activity Timeline**. | *"Every state transition, correlation ID, and payment status is immutably logged. Transparent, reproducible, and ready for real commerce."* |

---

## 6. Official PayPal Integration Reference

This project implements the official PayPal REST API v2 standards:
* **Orders v2 (`POST /v2/checkout/orders`):** Configured with `intent: "AUTHORIZE"`, `application_context` (`brand_name`, `return_url`, `cancel_url`), and server-bound amounts.
* **Order Authorize (`POST /v2/checkout/orders/{id}/authorize`):** Places the authorization hold on PayPal rails.
* **Payments v2 Capture (`POST /v2/payments/authorizations/{id}/capture`):** Delayed capture with `final_capture: true`, `Prefer: return=representation`, and `PayPal-Request-Id` idempotency.
* **Authorization Void (`POST /v2/payments/authorizations/{id}/void`):** Immediate release of held funds upon buyer cancellation.
* **Model Context Protocol (MCP):** Compatible with official PayPal Agent Toolkit schemas while preserving strict backend capture gates.

---

## 7. License

Distributed under the Apache 2.0 License. See `LICENSE` for details.
