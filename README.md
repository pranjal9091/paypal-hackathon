# Outcome Exchange

> **PayPal AI Hackathon 2026** — Buyer-Governed Multi-Agent AI Fulfillment with PayPal Authorization Hold & Independent Deterministic Verification.

---

## What is Outcome Exchange?

In autonomous AI commerce, agents should not have unilateral authority to spend money or settle their own invoices. 

**Outcome Exchange** is an outcome-based fulfillment system where:
1. A **Buyer** structures an outcome agreement with explicit, non-subjective acceptance criteria.
2. The buyer places a real **PayPal Sandbox Authorization Hold** (`intent: "AUTHORIZE"`). Funds are held securely on PayPal rails—**never captured prematurely**.
3. Specialized worker agents (Localization Agent, Content Agent, QA Agent) execute bounded tasks producing a multi-artifact deliverable bundle.
4. An **Automated Deterministic Verifier** independently validates the deliverable bundle (JSON syntax, required-key parity, variable placeholder retention like `{email}`, Markdown document structure, mandatory sections, word count bounds, and unsupported claim scans).
5. A **QA Agent** provides qualitative cross-artifact review, which is recorded informatively and **cannot bypass or weaken deterministic gates**.
6. An **Authoritative Backend Payment Gate** requires all mandatory verification criteria to pass AND explicit human buyer sign-off before executing `POST /v2/payments/authorizations/{id}/capture`. If deliverables fail or prompt injection is attempted, the hold is voided or re-executed at zero cost.

---

## Milestone 2: Multi-Agent Execution & Multi-Artifact Verification

Milestone 2 expands the foundational vertical slice into a full multi-agent workflow:

### 1. Three Specialist Agents
* **Localization Agent**: Produces `es_translations.json`. Preserves 100% of source keys and curly-brace placeholders (`{user}`, `{email}`, `{count}`, `{company}`).
* **Content Agent**: Produces `landing_page_es.md`. Generates high-converting Spanish landing page copy with an H1 title and four required H2 sections (*El Problema*, *La Solución*, *Características Principales*, *Llamado a la Acción*), bound to 120–500 words with factual claim safeguards.
* **QA Agent**: Produces `qa_report.json`. Reviews cross-artifact terminology, claim safety, and voice consistency. **Separation of Powers**: QA findings are informative (`evaluator="qa_agent"`, `is_mandatory=false`) and cannot override deterministic checks.

### 2. Real AI with Honest Fallbacks (`llm_client.py`)
* Server-side LLM client supporting Google Gemini and OpenAI when API keys are configured.
* Bounded retries and timeouts (default: 30s).
* Transparently labeled deterministic fallbacks (`provider="deterministic-fallback"`, `mode="fallback"`) when credentials are unset or provider calls fail. Fallback outputs are never misrepresented as live AI.

### 3. Independent Multi-Artifact Verification Engine (`deterministic_verifier.py`)
* **Bundle Completeness**: Verifies all required artifacts exist.
* **Translation Checks**: Valid JSON, exact key coverage, unexpected key policy, non-empty strings, placeholder preservation.
* **Landing Page Checks**: H1 title presence, four mandatory H2 sections, word count range [120, 500], and scanning for unsupported financial/regulatory claims.
* **Fail-Closed Policy**: If any mandatory check fails, `target_state` is set to `VERIFIED_FAILED`, and payment capture is locked.

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
# PayPal Sandbox Settings
PAYPAL_ENV=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret

# AI Provider Settings (Optional: defaults to transparent deterministic fallback)
LLM_PROVIDER=gemini       # Options: gemini, openai, mock
LLM_API_KEY=your_api_key  # Server-side only; never exposed to client
LLM_MODEL=gemini-2.5-flash
LLM_TIMEOUT_SECONDS=30
```
*Note: If credentials are not supplied, the backend operates in labeled Sandbox Mock Mode (`is_mock: true`) and Deterministic Fallback Mode (`is_fallback: true`), guaranteeing reliable offline evaluation.*

### 3. Launch Application
```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate in your browser to:
* **Interactive Multi-Agent Dashboard**: `http://localhost:8000/`
* **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`

---

## Running the Automated Test Suite

Run all 24 automated tests:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

### Verified Test Suite (24 Passing Tests)
1. `test_verifier_passes_on_valid_deliverable`: Validates JSON syntax, key parity, and placeholder preservation.
2. `test_verifier_fails_on_missing_key`: Fails when a required translation key is missing.
3. `test_verifier_fails_on_corrupted_placeholder`: Fails when `{email}` or `{user}` placeholder is corrupted.
4. `test_verifier_fails_on_empty_translation`: Fails on empty translation string.
5. `test_verifier_fails_on_invalid_json_syntax`: Fails on malformed JSON deliverable.
6. `test_multi_agent_bundle_generation_success`: Generates and verifies complete 3-artifact bundle.
7. `test_missing_landing_page_section_fails_verification`: Flags omitted mandatory landing page section.
8. `test_landing_page_word_count_violation`: Flags text below minimum word count.
9. `test_landing_page_unsupported_claim_detection`: Catches unsupported FDIC/banking claim.
10. `test_unexpected_keys_in_translations_fails_policy`: Flags unauthorized translation keys.
11. `test_incomplete_bundle_fails_verification`: Blocks verification when required artifact is missing.
12. `test_qa_agent_cannot_bypass_deterministic_checks`: Confirms QA approval cannot override failed deterministic check.
13. `test_llm_client_fallback_on_unavailable_credentials`: Confirms labeled fallback when credentials absent.
14. `test_demo_scenario_failure_and_recovery`: Full failure -> blocked capture -> recovery -> capture cycle.
15. `test_invalid_llm_json_output_handled_safely`: Catches malformed LLM JSON and falls back safely.
16. `test_llm_client_timeout_and_error_fallback`: Network timeout falls back to deterministic rule engine.
17. `test_illegal_state_transition_from_draft`: Prevents illegal state transitions.
18. `test_transition_to_awaiting_approval_requires_all_findings_passed`: Enforces state machine invariants.
19. `test_successful_end_to_end_vertical_slice`: End-to-end authorization, execution, verification, and capture.
20. `test_missing_deliverable_blocks_capture`: Missing deliverable prevents payment capture.
21. `test_capture_without_buyer_approval_rejected`: Capturing with `buyer_approved=False` returns HTTP 400.
22. `test_modified_amount_rejected`: Captured amount is strictly read from database record.
23. `test_duplicate_capture_handled_safely`: Repeated capture attempts return HTTP 409 Conflict.
24. `test_prompt_injection_input_untrusted`: Injected prompts in input remain untrusted and cannot alter payment state.

---

## Demo Scenarios

### Happy Path Demo
1. Open `http://localhost:8000/`.
2. Click **Create Contract ($40.00)**.
3. In Step 2, click **1. Create Hold Order**, then **2. Confirm Authorization Hold**. Funds are authorized on PayPal rails.
4. In Step 3, click **▶ Run Multi-Agent Team (Happy Path)**. All three agents generate their deliverables (`es_translations.json`, `landing_page_es.md`, `qa_report.json`).
5. In Step 4, click **Run Full Bundle Verification**. All 10 mandatory checks pass; QA review verdict is recorded. Contract transitions to `AWAITING_BUYER_APPROVAL`.
6. In Step 5, click **Approve Bundle & Capture $40.00**. Payment capture is released and immutable audit receipt is rendered.

### Failure and Recovery Demo
1. Create a contract and confirm the authorization hold ($40.00).
2. In Step 3, click **Simulate Missing Section (Landing Page)**.
3. In Step 4, click **Run Full Bundle Verification**. Verification fails with `landing_page_required_sections` failed. Contract state moves to `VERIFIED_FAILED`.
4. In Step 5, verify that **Capture is Strictly Blocked** (button disabled, API returns HTTP 400 if attempted).
5. In Step 3, click **▶ Run Multi-Agent Team (Happy Path)** to re-execute with clean content.
6. In Step 4, click **Run Full Bundle Verification**. Re-verification passes and unlocks the payment gate.
7. In Step 5, click **Approve Bundle & Capture $40.00**. Capture completes successfully.

---

## License

Apache License 2.0.
