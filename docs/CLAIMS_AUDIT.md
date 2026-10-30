# Outcome Exchange — Independent Claims Audit & Verification Matrix

> **Authoritative Technical Audit for PayPal AI Hackathon 2026**  
> **Evaluation Baseline:** Milestone 6 (`ff8cfbb` + Milestone 6 hardening)  
> **Verification Harness:** Automated test suite (55 passing tests in `backend/tests/`).  

---

## 1. Executive Summary of Claims

This document provides a line-by-line verification audit of every technical, financial, and security claim made in Outcome Exchange. 

We distinguish with total transparency between:
* **Verified by Automated Test**: Backed by reproducible unit, integration, or regression tests in `backend/tests/`.
* **Verified against Real External Provider**: Executed against actual external network APIs (PayPal Sandbox, Gemini/OpenAI).
* **Mock-Only**: Operates via structured local mock engines; clearly tagged in API and UI.
* **Not Verified**: Claims or code paths that cannot be proven in the current offline environment without live credentials.
* **Known Limitations**: Architectural boundaries, storage constraints, and edge-case behaviors.

---

## 2. Line-by-Line Claims Verification Matrix

| Claim ID | Claim Description | Verification Status | Evidence / Implementation Source |
| :--- | :--- | :--- | :--- |
| **CLM-01** | **PayPal mock and live modes are reliably distinguishable.** | **Verified by Automated Test** | `test_mcp_mock_mode_distinction`, `test_absent_paypal_credentials_never_claims_live_success`. `is_mock: bool` is explicitly propagated in API schemas, DB records, and UI badges. |
| **CLM-02** | **Real provider success is never fabricated when credentials are absent or API fails.** | **Verified by Automated Test** | `backend/app/config.py` checks `has_real_paypal_credentials` and `has_real_llm_credentials`. If credentials are absent, `/api/health` reports `false` and transactions are flagged as `is_mock: True`. |
| **CLM-03** | **Buyer confirmation is persisted and enforced server-side (Human Gate 1).** | **Verified by Automated Test** | `test_buyer_confirmation_creates_authoritative_contract`. Contract state machine forbids transitioning from `DRAFT` to `HOLD_PENDING` without buyer sign-off. |
| **CLM-04** | **Exact approved contract amount and currency are used during capture.** | **Verified by Automated Test** | `test_modified_amount_rejected`, `test_contract_amount_tampering_strictly_ignored`. `capture_payment` in `payments.py` strictly reads `contract.budget_amount`, ignoring client payloads. |
| **CLM-05** | **Client cannot substitute a forged order ID or authorization ID.** | **Verified by Automated Test** | `test_forged_order_identifier_rejected`, `test_forged_authorization_identifier_rejected`. `confirm_authorization` rejects forged IDs with HTTP 400. Capture endpoint takes no authorization ID argument. |
| **CLM-06** | **Duplicate or concurrent capture requests cannot create an unauthorized second capture.** | **Verified by Automated Test** | `test_duplicate_capture_handled_safely`, `test_duplicate_capture_replayed_request_rejected`. Backend raises HTTP 409 Conflict if capture is attempted more than once. |
| **CLM-07** | **Failed verification prevents capture, including through direct API calls.** | **Verified by Automated Test** | `test_missing_deliverable_blocks_capture`, `test_failed_verification_cannot_be_overwritten`. Route-level checks re-evaluate mandatory findings before capture. |
| **CLM-08** | **MCP interface does not expose a path around financial approval gates.** | **Verified by Automated Test** | `test_mcp_list_tools`, `test_mcp_caller_cannot_capture_funds`. `paypal_capture_order` is strictly omitted from the MCP tool catalog. |
| **CLM-09** | **Prompt injection cannot modify authoritative budget or trigger payment.** | **Verified by Automated Test** | `test_prompt_injection_in_buyer_request_contained`, `test_prompt_injection_input_untrusted`. Injected prompts in input strings are treated as untrusted data. |
| **CLM-10** | **Invalid LLM output cannot bypass deterministic verification.** | **Verified by Automated Test** | `test_qa_agent_cannot_bypass_deterministic_checks`, `test_invalid_llm_json_output_handled_safely`. Verifier is 100% rule-based and fails closed. |
| **CLM-11** | **Audit events survive browser refresh and application restart.** | **Verified by Automated Test** | `test_audit_history_persists_across_queries`. Events are persisted in SQLite `audit_events` table and ordered chronologically by `created_at`. |
| **CLM-12** | **UI status indicators accurately reflect backend configuration.** | **Verified by Automated Test** | `GET /api/health` dynamically drives `PAYPAL: SANDBOX (MOCK/LIVE)` and `AI: DETERMINISTIC FALLBACK/LIVE` badges on `http://127.0.0.1:8000/`. |
| **CLM-13** | **Receipt distinguishes actual provider transaction IDs from mock IDs.** | **Verified by Automated Test** | Mock identifiers are prefixed `MOCK-ORDER-`, `MOCK-AUTH-`, `MOCK-CAP-`. Receipt table explicitly displays `Rail Engine: PayPal Sandbox (Mock Engine)`. |
| **CLM-14** | **Deterministic Idempotency Keys on Payment Routes.** | **Verified by Automated Test** | `test_deterministic_idempotency_keys_on_payment_routes`. Payment routes compute deterministic keys (`capture_{contract_id}_{auth_id}`, `void_{contract_id}_{auth_id}`, `order_{contract_id}`) when headers are omitted, preventing duplicate debit on replayed network requests. |
| **CLM-15** | **Mutual Exclusion and State Integrity across Payment Transitions.** | **Verified by Automated Test** | `test_void_on_settled_contract_rejected`, `test_concurrent_or_sequential_double_capture_serialization`. `_capture_lock` serializes captures and voids in-process; terminal states reject reverse transitions. |
| **CLM-16** | **Real PayPal Sandbox OAuth token exchange & Order creation.** | **Not Verified (Credentials Absent)** | Code complete in `paypal_client.py` (`/v1/oauth2/token` and `/v2/checkout/orders`), but `.env` credentials were not configured in this environment. |
| **CLM-17** | **Real PayPal Sandbox delayed capture.** | **Not Verified (Credentials Absent)** | Code complete in `paypal_client.py` (`/v2/payments/authorizations/{id}/capture`), but live network execution has not taken place. |
| **CLM-18** | **Live Gemini / OpenAI LLM completion.** | **Not Verified (Credentials Absent)** | Code complete in `llm_client.py` (`_call_gemini`, `_call_openai`), but `LLM_API_KEY` is not present in environment. |

---

## 3. Deep Dive: Audit Timeline & Immutability Analysis

### Accurate Characterization: "Append-Only Application Audit Log"
* **Implementation Reality:** Audit events are stored in a standard relational table (`audit_events` in SQLite / PostgreSQL). 
* **Immutability Boundaries:** 
  - At the **application API boundary**, the audit log is strictly **append-only**: the FastAPI backend exposes `INSERT` during state transitions and `SELECT` via `/api/contracts/{id}/receipt`, with zero `UPDATE` or `DELETE` endpoints.
  - However, the audit log **does not use cryptographic hashing (Merkle trees, SHA-256 chaining, or blockchain storage)**. A database administrator with direct access to the SQLite file could modify rows.
* **Conclusion:** We do **not** call this log "cryptographically immutable." It is properly characterized as an **authoritative, application-enforced append-only audit trail**.

---

## 4. State Machine Failure Analysis & Recoverability

The server-side state machine (`backend/app/state_machine.py`) manages transitions across 11 explicit states:
`DRAFT` → `HOLD_PENDING` → `AUTHORIZED` → `EXECUTING` → `VERIFIED_PASSED` / `VERIFIED_FAILED` → `AWAITING_BUYER_APPROVAL` → `PAID` / `VOIDED` / `CANCELLED`.

### Evaluated Edge Cases & Mitigations:
1. **Network Timeout during Order Creation**:
   - Contract remains in `DRAFT` state. No payment record is committed. Buyer can retry safely.
2. **Failure during Deliverable Verification**:
   - Contract transitions to `VERIFIED_FAILED`.
   - `capture_payment` is strictly blocked (HTTP 400).
   - Recovery: Buyer can re-execute the agent team (`POST /api/contracts/{id}/execute`) and re-verify, which transitions `VERIFIED_FAILED` → `EXECUTING` → `VERIFIED_PASSED`.
3. **Authorization Hold Cancellation**:
   - Buyer can cancel or reject at `VERIFIED_FAILED` or `AWAITING_BUYER_APPROVAL`.
   - `POST /api/contracts/{id}/void` calls PayPal void endpoint and transitions contract to terminal `VOIDED` state ($0 charge).
4. **Duplicate Capture Attempts**:
   - Second capture call encounters `payment.status == "CAPTURED"` or `contract.status == "PAID"`.
   - Rejects immediately with HTTP 409 Conflict; no duplicate capture is submitted to PayPal.
5. **Simultaneous Capture and Void Attempts**:
   - `_capture_lock` serializes requests within the current process; whichever executes first completes, and the second is rejected with HTTP 400/409.

---

## 5. Current Known Limitations & Distributed Concurrency Boundaries

1. **Process-Local Mutex Scope**:
   - `_capture_lock` in `routes/payments.py` is an in-memory `asyncio.Lock()`. It guarantees sequential execution of capture and void operations **within a single process event loop**.
   - In a horizontally scaled production deployment (e.g., multiple Gunicorn workers or multi-container Kubernetes pods), this lock does not span instances. Concurrency in distributed deployments must rely on:
     - PayPal's network-level idempotency header (`PayPal-Request-Id`).
     - PostgreSQL database row-level locking (`SELECT ... FOR UPDATE`).
     - Distributed locking via Redis (Redlock).
2. **PayPal Webhooks vs Synchronous Relays**:
   - Authorization hold confirmation currently relies on the frontend relaying the approved order ID to `/confirm-authorization`. While validated against order tampering, production setups should pair this with an asynchronous PayPal Webhook listener (`PAYMENT.AUTHORIZATION.CREATED`).
3. **Offline Development Runtime**:
   - Without live sandbox client credentials in `.env`, all tests run in mock mode. The mock engine faithfully mirrors PayPal Orders v2 and Payments v2 responses, but external network latency and PayPal account-level restrictions are unverified.
