# Outcome Exchange

> **PayPal AI Hackathon 2026** — Buyer-Governed Multi-Agent AI Fulfillment with PayPal Authorization Hold, Official PayPal Agent Toolkit (MCP), and Independent Deterministic Verification.

---

## What is Outcome Exchange?

In autonomous AI commerce, agents should not have unilateral authority to spend money or settle their own invoices. 

**Outcome Exchange** is an outcome-based fulfillment system where:
1. A **Buyer** describes a business goal in natural language to a **Buyer Agent**, which extracts deliverables, generates acceptance criteria with explicit rationale, and prepares a structured contract proposal.
2. The human buyer reviews and explicitly signs off on the proposal (**Human Gate 1**).
3. The Buyer Agent initiates an official **PayPal Agent Toolkit** tool call (`paypal_create_order` via Model Context Protocol) with `intent: "AUTHORIZE"`. Funds are held securely on PayPal rails—**never captured prematurely**.
4. Specialized worker agents (Localization Agent, Content Agent, QA Agent) execute bounded tasks producing a multi-artifact deliverable bundle (`es_translations.json`, `landing_page_es.md`, `qa_report.json`).
5. An **Automated Deterministic Verifier** independently validates the deliverable bundle (JSON syntax, required-key parity, variable placeholder retention like `{email}`, Markdown document structure, mandatory sections, word count bounds, and unsupported claim scans).
6. A **QA Agent** provides qualitative cross-artifact review, which is recorded informatively and **cannot bypass or weaken deterministic gates**.
7. An **Authoritative Backend Payment Gate (Human Gate 2)** strictly enforces that all mandatory verification criteria pass AND the human buyer gives explicit sign-off before executing `POST /v2/payments/authorizations/{id}/capture`. If deliverables fail or prompt injection is attempted, the hold is voided or re-executed at zero cost.

---

## Milestone 3: PayPal-Native Buyer Agent & MCP Integration

Milestone 3 introduces autonomous contract formulation and official PayPal Agent Toolkit integration while strictly preserving human-controlled financial safety:

### 1. Conversational Buyer Agent (`buyer_agent.py`, `/api/buyer/propose`)
* Converts natural-language requests into structured digital contracts.
* Extracts deliverables, required keys, acceptance criteria, and budget.
* Flags missing requirements or contradictory terms and asks for clarification.
* Explains the technical and business rationale behind selected criteria.
* Produces transparent explanations for payment release gate decisions.

### 2. Official PayPal Agent Toolkit & Model Context Protocol (MCP) (`paypal_toolkit.py`, `/api/mcp/`)
* Exposes official PayPal Agent Toolkit tools:
  * `paypal_create_order`: Creates a PayPal checkout order configured for authorization hold (`intent: "AUTHORIZE"`).
  * `paypal_get_order`: Inspects order status.
  * `paypal_authorize_order`: Confirms authorization hold.
* **Separation of Powers**: Payment capture (`paypal_capture_order`) is intentionally **omitted** from the agent tool catalog. Autonomous agents cannot authorize their own settlement.
* Validates inputs against Pydantic schemas, records correlation IDs (`mcp-corr-*`), and tags execution with live vs mock status.

### 3. Preserved Human-Controlled Payment Gate
* **Gate 1 (Contract Formation)**: The buyer must explicitly review and confirm the contract terms.
* **Gate 2 (Deliverable Release)**: The backend guarantees funds can only be captured when:
  1. Complete deliverable bundle exists.
  2. All mandatory deterministic checks pass.
  3. Authorization hold is active.
  4. Human buyer clicks "Approve Deliverables & Capture".

---

## Local Setup & Quickstart

### Prerequisites
* Python 3.12+ installed
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
Available environment variables:
```env
# PayPal Sandbox Settings (Optional: defaults to transparent Sandbox Mock)
PAYPAL_ENV=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret

# AI Provider Settings (Optional: defaults to transparent deterministic fallback)
LLM_PROVIDER=gemini       # Options: gemini, openai, mock
LLM_API_KEY=your_api_key  # Server-side only; never exposed to client
LLM_MODEL=gemini-2.5-flash
LLM_TIMEOUT_SECONDS=30
```
*Note: If credentials are not supplied, the backend operates in labeled Sandbox Mock Mode (`is_mock: true`) and Deterministic Fallback Mode (`is_fallback: true`), guaranteeing reliable offline evaluation and hackathon judging.*

### 3. Launch Application
```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate in your browser to:
* **Interactive Multi-Agent Dashboard**: `http://localhost:8000/`
* **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`

---

## Running the Automated Test Suite

Run all 36 automated tests:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

### Verified Test Suite (36 Passing Tests)
1. `test_natural_language_request_converted_into_valid_proposal`: Buyer Agent extracts deliverables, budget, and criteria.
2. `test_missing_requirements_trigger_clarification`: Incomplete request prompts clarification dialog.
3. `test_contradictory_contract_requirements_handled`: Flags contradictory requests ($0 budget for paid work).
4. `test_budget_tampering_rejected_by_backend`: Backend rejects zero/negative budget tampering.
5. `test_buyer_confirmation_creates_authoritative_contract`: Contract is created only after explicit confirmation (Gate 1).
6. `test_mcp_list_tools`: Exposes official PayPal Agent Toolkit tools; verifies capture tool is omitted.
7. `test_mcp_create_order_tool_call`: MCP tool creates authorization order and returns correlation ID.
8. `test_mcp_input_validation_failure`: Validates MCP arguments against Pydantic schema.
9. `test_buyer_agent_cannot_bypass_verification_gate`: Proves agent cannot capture payment when checks fail.
10. `test_prompt_injection_in_buyer_request_contained`: Injected prompts in input cannot override budget or policy.
11. `test_mcp_tool_timeout_and_error_handling`: Gateway timeouts return clean structured MCP error.
12. `test_mcp_mock_mode_distinction`: Mock vs live execution mode is explicitly tagged.
13. `test_verifier_passes_on_valid_deliverable`: Validates JSON syntax, key parity, and placeholder preservation.
14. `test_verifier_fails_on_missing_key`: Fails when a required translation key is missing.
15. `test_verifier_fails_on_corrupted_placeholder`: Fails when `{email}` or `{user}` placeholder is corrupted.
16. `test_verifier_fails_on_empty_translation`: Fails on empty translation string.
17. `test_verifier_fails_on_invalid_json_syntax`: Fails on malformed JSON deliverable.
18. `test_multi_agent_bundle_generation_success`: Generates and verifies complete 3-artifact bundle.
19. `test_missing_landing_page_section_fails_verification`: Flags omitted mandatory landing page section.
20. `test_landing_page_word_count_violation`: Flags copy below minimum word count.
21. `test_landing_page_unsupported_claim_detection`: Catches unsupported FDIC/banking claims.
22. `test_unexpected_keys_in_translations_fails_policy`: Flags unauthorized translation keys.
23. `test_incomplete_bundle_fails_verification`: Blocks verification when required artifact is missing.
24. `test_qa_agent_cannot_bypass_deterministic_checks`: Proves QA approval cannot override failed deterministic check.
25. `test_llm_client_fallback_on_unavailable_credentials`: Confirms labeled fallback when credentials absent.
26. `test_demo_scenario_failure_and_recovery`: Full failure -> blocked capture -> recovery -> capture cycle.
27. `test_invalid_llm_json_output_handled_safely`: Catches malformed LLM JSON and falls back safely.
28. `test_llm_client_timeout_and_error_fallback`: Network timeout triggers bounded fallback.
29. `test_illegal_state_transition_from_draft`: Prevents illegal state transitions.
30. `test_transition_to_awaiting_approval_requires_all_findings_passed`: Enforces state machine invariants.
31. `test_successful_end_to_end_vertical_slice`: End-to-end authorization, execution, verification, and capture.
32. `test_missing_deliverable_blocks_capture`: Missing deliverable prevents payment capture.
33. `test_capture_without_buyer_approval_rejected`: Capturing with `buyer_approved=False` returns HTTP 400.
34. `test_modified_amount_rejected`: Captured amount is strictly read from database record.
35. `test_duplicate_capture_handled_safely`: Repeated capture attempts return HTTP 409 Conflict.
36. `test_prompt_injection_input_untrusted`: Injected prompts in input remain untrusted and cannot alter payment state.

---

## Live Demonstration Guide

### Happy Path: Conversational AI Procurement to Settled Outcome
1. Open `http://localhost:8000/`.
2. In **Step 1 (Buyer Agent)**, click **Analyze & Propose Contract**. The agent reviews the natural-language request and extracts the deliverables, budget ($40.00 USD), and acceptance criteria rationale.
3. Click **Buyer Sign-Off: Confirm Terms & Create Contract ($40.00)** (Human Gate 1).
4. In **Step 2 (PayPal Agent Toolkit & MCP)**, click **1. Create Order via PayPal Agent Toolkit**, then **2. Confirm Authorization Hold**. Funds are authorized on PayPal rails.
5. In **Step 3 (Multi-Agent Fulfillment Team)**, click **▶ Run Multi-Agent Team (Happy Path)**. Localization, Content, and QA agents generate `es_translations.json`, `landing_page_es.md`, and `qa_report.json`.
6. In **Step 4 (Deterministic Verification)**, click **Run Full Bundle Verification**. All 10 mandatory checks pass.
7. In **Step 5 (Payment Release Gate)**, review the Buyer Agent reasoning and click **Approve Deliverables & Capture $40.00** (Human Gate 2).
8. In **Step 6 (Auditable Reasoning Timeline)**, inspect the complete timeline from prompt to settled receipt.

### Blocked Payment Demo: Verification Failure Prevents Release
1. Create and confirm a contract, then place the $40.00 PayPal authorization hold.
2. In **Step 3**, click **Simulate Missing Section**.
3. In **Step 4**, click **Run Full Bundle Verification**. Verification fails with `landing_page_required_sections` failed. Contract moves to `VERIFIED_FAILED`.
4. In **Step 5**, verify that the Buyer Agent reasoning declares **"Payment Capture Strictly Blocked: Mandatory Verification Failed"** and the capture button is disabled (API rejects capture with HTTP 400).
5. In **Step 3**, click **▶ Run Multi-Agent Team (Happy Path)** to re-execute cleanly.
6. In **Step 4**, re-run verification. All checks pass, unlocking the release gate.
7. In **Step 5**, click **Approve Deliverables & Capture $40.00**. Capture succeeds.

---

## License

Apache License 2.0.
