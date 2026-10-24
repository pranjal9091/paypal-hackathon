import json
import pytest
from app.state_machine import ContractState
from app.verifier.deterministic_verifier import DeterministicVerifier
from app.llm_client import LLMClient

SOURCE_STRINGS = {
    "app_title": "TidyLedger — Modern Cloud Accounting",
    "login_button": "Log in to your account",
    "welcome_message": "Welcome back, {user}! Your financial dashboard is up to date.",
    "password_reset_notice": "A password recovery link has been sent to {email}.",
    "invoice_summary": "You have {count} pending invoices awaiting approval for {company}."
}

def create_contract(client, budget="40.00", currency="USD"):
    res = client.post("/api/contracts", json={
        "title": "Spanish Launch Kit Multi-Agent Contract",
        "description": "Spanish localization and landing page copy with QA verification for TidyLedger",
        "budget_amount": budget,
        "currency": currency,
        "source_strings": SOURCE_STRINGS
    })
    assert res.status_code == 200
    return res.json()

# Test 1: Full multi-agent execution generates all 3 deliverables and verifies bundle
def test_multi_agent_bundle_generation_success(client):
    contract = create_contract(client)
    cid = contract["id"]

    # Place hold
    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-1"})

    # Execute Multi-Agent Workflow
    exec_res = client.post(f"/api/contracts/{cid}/execute")
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert len(exec_data["deliverables"]) == 3

    filenames = [d["filename"] for d in exec_data["deliverables"]]
    assert "es_translations.json" in filenames
    assert "landing_page_es.md" in filenames
    assert "qa_report.json" in filenames

    # Verify bundle
    verify_res = client.post(f"/api/contracts/{cid}/verify")
    assert verify_res.status_code == 200
    report = verify_res.json()
    assert report["passed"] is True
    assert report["failed_checks"] == 0

    # Confirm capture succeeds with buyer approval
    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 200
    assert cap_res.json()["status"] == "CAPTURED"

# Test 2: Missing required landing page section fails verification and blocks capture
def test_missing_landing_page_section_fails_verification(client):
    contract = create_contract(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-1"})

    # Execute with simulated missing section (CTA omitted)
    client.post(f"/api/contracts/{cid}/execute?simulate_missing_section=true")

    # Verify -> MUST FAIL
    verify_res = client.post(f"/api/contracts/{cid}/verify")
    assert verify_res.status_code == 200
    report = verify_res.json()
    assert report["passed"] is False

    failed_criteria = [f["criterion_name"] for f in report["findings"] if not f["passed"]]
    assert "landing_page_required_sections" in failed_criteria

    # Capture MUST BE BLOCKED
    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 400

# Test 3: Landing page word count violation fails verification and blocks capture
def test_landing_page_word_count_violation(client):
    contract = create_contract(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-1"})

    # Execute with simulated word-count violation (15 words)
    client.post(f"/api/contracts/{cid}/execute?simulate_word_count_violation=true")

    verify_res = client.post(f"/api/contracts/{cid}/verify")
    report = verify_res.json()
    assert report["passed"] is False
    failed_criteria = [f["criterion_name"] for f in report["findings"] if not f["passed"]]
    assert "landing_page_word_count" in failed_criteria

    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 400

# Test 4: Unsupported regulatory/banking claims in landing page are detected
def test_landing_page_unsupported_claim_detection(client):
    contract = create_contract(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-1"})

    # Execute with unsupported claim injection
    client.post(f"/api/contracts/{cid}/execute?simulate_unsupported_claim=true")

    verify_res = client.post(f"/api/contracts/{cid}/verify")
    report = verify_res.json()
    assert report["passed"] is False
    failed_criteria = [f["criterion_name"] for f in report["findings"] if not f["passed"]]
    assert "landing_page_factual_claim_safety" in failed_criteria

    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 400

# Test 5: Unexpected keys injected into translations fail verification policy
def test_unexpected_keys_in_translations_fails_policy():
    malicious_translations = json.dumps({
        "app_title": "TidyLedger",
        "login_button": "Iniciar sesión",
        "welcome_message": "Bienvenido, {user}!",
        "password_reset_notice": "Enlace a {email}",
        "invoice_summary": "Facturas para {company}: {count}",
        "unauthorized_admin_key": "true" # Extra key!
    })
    passed, findings = DeterministicVerifier.verify_translations(SOURCE_STRINGS, malicious_translations)
    assert passed is False
    unexpected_finding = next(f for f in findings if f.criterion_name == "unexpected_keys_policy")
    assert unexpected_finding.passed is False
    assert "unauthorized_admin_key" in unexpected_finding.details

# Test 6: Incomplete bundle (missing deliverable file) fails verification
def test_incomplete_bundle_fails_verification():
    deliverables = {
        "es_translations.json": "{}"
        # landing_page_es.md is missing!
    }
    passed, findings = DeterministicVerifier.verify_bundle(SOURCE_STRINGS, deliverables)
    assert passed is False
    bundle_finding = next(f for f in findings if f.criterion_name == "bundle_deliverable_completeness")
    assert bundle_finding.passed is False
    assert "landing_page_es.md" in bundle_finding.details

# Test 7: QA Agent opinion cannot bypass failed deterministic checks
def test_qa_agent_cannot_bypass_deterministic_checks(client):
    contract = create_contract(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-1"})

    # Cause deterministic failure (missing section)
    client.post(f"/api/contracts/{cid}/execute?simulate_missing_section=true")

    verify_res = client.post(f"/api/contracts/{cid}/verify")
    report = verify_res.json()
    assert report["passed"] is False

    # Check that QA Agent finding was recorded as non-mandatory
    qa_finding = next(f for f in report["findings"] if f["evaluator"] == "qa_agent")
    assert qa_finding["is_mandatory"] is False

    # Attempt capture: MUST BE BLOCKED regardless of QA report
    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 400

# Test 8: LLM client transparent fallback when credentials unavailable
@pytest.mark.asyncio
async def test_llm_client_fallback_on_unavailable_credentials():
    test_client = LLMClient()
    result = await test_client.generate(
        prompt="Translate this",
        fallback_content="Fallback Content",
        force_fallback=True
    )
    assert result.is_fallback is True
    assert result.mode == "fallback"
    assert result.provider == "deterministic-fallback"
    assert result.content == "Fallback Content"

# Test 9: Complete demo scenario: Failure -> Recovery
def test_demo_scenario_failure_and_recovery(client):
    contract = create_contract(client)
    cid = contract["id"]

    # 1. Place Hold
    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-DEMO"})

    # 2. Run with failure mode (missing required section)
    client.post(f"/api/contracts/{cid}/execute?simulate_missing_section=true")
    verify_res = client.post(f"/api/contracts/{cid}/verify")
    assert verify_res.json()["passed"] is False

    # 3. Capture is strictly blocked
    blocked_cap = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert blocked_cap.status_code == 400

    # 4. Recovery: Re-execute with clean normal workflow
    recovery_exec = client.post(f"/api/contracts/{cid}/execute")
    assert recovery_exec.status_code == 200

    # 5. Re-verify -> Passes
    re_verify = client.post(f"/api/contracts/{cid}/verify")
    assert re_verify.json()["passed"] is True

    # 6. Capture is unlocked and succeeds!
    final_cap = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert final_cap.status_code == 200
    assert final_cap.json()["status"] == "CAPTURED"


# Test 10: Invalid LLM output is caught and safely falls back
@pytest.mark.asyncio
async def test_invalid_llm_json_output_handled_safely(monkeypatch):
    from unittest.mock import AsyncMock
    from app.llm_client import LLMResult
    from app.agents.localization_agent import LocalizationAgent

    source = {"app.title": "Outcome Exchange", "user.greeting": "Welcome, {user}!"}

    # Mock LLM returning malformed, non-JSON text
    mock_generate = AsyncMock(return_value=LLMResult(
        content="Here is your translation: {\"app.title\": ... wait this is invalid json!",
        provider="gemini",
        mode="live",
        model="gemini-2.5-flash",
        is_fallback=False
    ))
    monkeypatch.setattr("app.agents.localization_agent.llm_client.generate", mock_generate)

    res = await LocalizationAgent.execute(source_strings=source)
    assert res["is_fallback"] is True
    assert res["mode"] == "fallback"
    # Ensure fallback content was returned as valid JSON
    parsed = json.loads(res["content"])
    assert "app.title" in parsed
    assert "{user}" in parsed["user.greeting"]


# Test 11: Provider network timeout / error triggers clean bounded fallback
@pytest.mark.asyncio
async def test_llm_client_timeout_and_error_fallback(monkeypatch):
    test_client = LLMClient()
    monkeypatch.setattr(LLMClient, "is_live_configured", property(lambda self: True))
    monkeypatch.setattr(test_client, "provider", "gemini")

    # Mock _call_gemini throwing a Timeout error
    from unittest.mock import AsyncMock
    mock_call = AsyncMock(side_effect=TimeoutError("Request timed out after 30s"))
    monkeypatch.setattr(test_client, "_call_gemini", mock_call)

    result = await test_client.generate(
        prompt="Test prompt",
        fallback_content="Safe Fallback Text"
    )

    assert result.is_fallback is True
    assert result.mode == "fallback"
    assert result.provider == "deterministic-fallback"
    assert result.content == "Safe Fallback Text"
    assert "Request timed out" in result.error_detail

