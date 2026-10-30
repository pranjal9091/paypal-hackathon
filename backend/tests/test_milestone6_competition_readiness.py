import json
import pytest
from unittest.mock import AsyncMock
from app.state_machine import ContractState
from app.llm_client import LLMResult
from app.agents.buyer_agent import BuyerAgent, extract_json_object
from app.agents.localization_agent import LocalizationAgent
from app.agents.content_agent import ContentAgent
from app.agents.qa_agent import QAAgent

SAMPLE_SOURCE_STRINGS = {
    "app_title": "TidyLedger — Modern Cloud Accounting",
    "login_button": "Log in to your account",
    "welcome_message": "Welcome back, {user}!",
    "reset_notice": "Password link sent to {email}."
}

def create_contract_helper(client, budget="40.00", currency="USD"):
    res = client.post("/api/contracts", json={
        "title": "Milestone 6 Competition Validation Contract",
        "description": "Validation of AI robustness, idempotency, and concurrency controls",
        "budget_amount": budget,
        "currency": currency,
        "source_strings": SAMPLE_SOURCE_STRINGS
    })
    assert res.status_code == 200
    return res.json()

# 1. Deterministic Idempotency Keys when PayPal-Request-Id header is omitted
def test_deterministic_idempotency_keys_on_payment_routes(client, monkeypatch):
    contract = create_contract_helper(client)
    cid = contract["id"]

    captured_keys = {}

    from app.paypal_client import paypal_client

    original_create = paypal_client.create_order
    original_auth = paypal_client.authorize_order
    original_cap = paypal_client.capture_authorization
    original_void = paypal_client.void_authorization

    async def mock_create(amount, currency, reference_id, idempotency_key=None):
        captured_keys["create"] = idempotency_key
        return await original_create(amount, currency, reference_id, idempotency_key)

    async def mock_auth(order_id, idempotency_key=None):
        captured_keys["auth"] = idempotency_key
        return await original_auth(order_id, idempotency_key)

    async def mock_cap(authorization_id, amount, currency, idempotency_key=None):
        captured_keys["cap"] = idempotency_key
        return await original_cap(authorization_id, amount, currency, idempotency_key)

    monkeypatch.setattr(paypal_client, "create_order", mock_create)
    monkeypatch.setattr(paypal_client, "authorize_order", mock_auth)
    monkeypatch.setattr(paypal_client, "capture_authorization", mock_cap)

    # 1. Create order
    client.post(f"/api/contracts/{cid}/create-hold-order")
    assert captured_keys["create"] == f"order_{cid}"

    # 2. Confirm auth
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-TEST"})
    assert captured_keys["auth"] == f"auth_{cid}_MOCK-ORDER-TEST"

    # 3. Execute & Verify
    client.post(f"/api/contracts/{cid}/execute")
    client.post(f"/api/contracts/{cid}/verify")

    # 4. Capture
    cap_res = client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})
    assert cap_res.status_code == 200
    # Payment record authorization id is MOCK-AUTH-...
    payment = client.get(f"/api/contracts/{cid}/receipt").json()["payment"]
    auth_id = payment["paypal_authorization_id"]
    assert captured_keys["cap"] == f"capture_{cid}_{auth_id}"

# 2. Void Payment acquires mutex and rejects void on already settled contract
def test_void_on_settled_contract_rejected(client):
    contract = create_contract_helper(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-TEST"})
    client.post(f"/api/contracts/{cid}/execute")
    client.post(f"/api/contracts/{cid}/verify")
    client.post(f"/api/contracts/{cid}/capture", json={"buyer_approved": True})

    # Contract is now PAID. Attempting to void must be rejected with 400
    void_res = client.post(f"/api/contracts/{cid}/void")
    assert void_res.status_code == 400
    assert "Cannot void" in void_res.json()["detail"] or "CAPTURED" in void_res.json()["detail"]

# 3. Live LLM Markdown Fenced JSON parsed cleanly in LocalizationAgent
@pytest.mark.asyncio
async def test_localization_agent_parses_markdown_fenced_json(monkeypatch):
    source = {"app_title": "TidyLedger", "welcome_user": "Welcome, {user}!"}
    fenced_output = """```json
{
  "app_title": "TidyLedger — Contabilidad Inteligente",
  "welcome_user": "¡Bienvenido, {user}!"
}
```"""
    mock_generate = AsyncMock(return_value=LLMResult(
        content=fenced_output,
        provider="gemini",
        mode="live",
        model="gemini-2.5-flash",
        is_fallback=False
    ))
    monkeypatch.setattr("app.agents.localization_agent.llm_client.generate", mock_generate)

    res = await LocalizationAgent.execute(source_strings=source)
    assert res["is_fallback"] is False
    assert res["mode"] == "live"
    parsed = json.loads(res["content"])
    assert parsed["app_title"] == "TidyLedger — Contabilidad Inteligente"
    assert "{user}" in parsed["welcome_user"]

# 4. Live LLM Markdown Fenced Markdown parsed cleanly in ContentAgent
@pytest.mark.asyncio
async def test_content_agent_cleans_fenced_markdown(monkeypatch):
    fenced_copy = """```markdown
# TidyLedger — Contabilidad Inteligente para Empresas

## El Problema
Gestionar las finanzas de un negocio emergente suele convertirse en una pesadilla de hojas de cálculo desordenadas.

## La Solución
TidyLedger centraliza, automatiza y simplifica toda la contabilidad de tu empresa en una única plataforma en la nube.

## Características Principales
- Facturación rápida con cálculo automático de impuestos.
- Conciliación bancaria en tiempo real.
- Reportes financieros comprensibles.
- Acceso seguro para contadores y administradores.

## Llamado a la Acción
Comienza hoy mismo a tomar el control total de las finanzas de tu negocio. Regístrate ahora con 14 días gratis.
```"""
    mock_generate = AsyncMock(return_value=LLMResult(
        content=fenced_copy,
        provider="gemini",
        mode="live",
        model="gemini-2.5-flash",
        is_fallback=False
    ))
    monkeypatch.setattr("app.agents.content_agent.llm_client.generate", mock_generate)

    res = await ContentAgent.execute(contract_title="TidyLedger", contract_desc="Contabilidad SaaS")
    assert res["is_fallback"] is False
    assert res["mode"] == "live"
    assert res["content"].startswith("# ")
    assert "## El Problema" in res["content"]

# 5. Live LLM QA Report Markdown Fenced JSON parsed cleanly in QAAgent
@pytest.mark.asyncio
async def test_qa_agent_parses_fenced_qa_report(monkeypatch):
    fenced_qa = """```json
{
  "verdict": "PASS",
  "score": 98,
  "review_summary": "High terminology coherence across deliverables.",
  "consistency_check": true,
  "checks": [
    {"name": "formatting", "status": "PASS", "details": "Well structured"}
  ],
  "suggestions": []
}
```"""
    mock_generate = AsyncMock(return_value=LLMResult(
        content=fenced_qa,
        provider="gemini",
        mode="live",
        model="gemini-2.5-flash",
        is_fallback=False
    ))
    monkeypatch.setattr("app.agents.qa_agent.llm_client.generate", mock_generate)

    res = await QAAgent.review(translations_content="{}", landing_content="# Test")
    assert res["is_fallback"] is False
    assert res["mode"] == "live"
    parsed = json.loads(res["content"])
    assert parsed["verdict"] == "PASS"
    assert parsed["score"] == 98

# 6. Buyer Agent Live LLM Proposal Enrichment handles structured proposal
@pytest.mark.asyncio
async def test_buyer_agent_live_enrichment(monkeypatch):
    from app.llm_client import LLMClient, llm_client
    monkeypatch.setattr(LLMClient, "is_live_configured", property(lambda self: True))

    llm_response = """```json
{
  "title": "Custom SaaS Launch Suite",
  "description": "Enterprise Spanish translation and landing page copy",
  "proposed_budget": "40.00",
  "currency": "USD",
  "requested_deliverables": ["es_translations.json", "landing_page_es.md", "qa_report.json"],
  "clarification_needed": null,
  "acceptance_criteria_rationale": "High-fidelity enterprise standards."
}
```"""
    mock_gen = AsyncMock(return_value=LLMResult(
        content=llm_response,
        provider="gemini",
        mode="live",
        model="gemini-2.5-flash",
        is_fallback=False
    ))
    monkeypatch.setattr(llm_client, "generate", mock_gen)

    proposal = await BuyerAgent.formulate_proposal("Launch kit with budget: $40.00")
    assert proposal.is_valid is True
    assert proposal.title == "Custom SaaS Launch Suite"
    assert proposal.budget_amount == "40.00"
    assert "High-fidelity enterprise standards." in proposal.acceptance_criteria_rationale

# 7. Audit records capture is_fallback and model explicitly
def test_audit_records_distinguish_model_and_fallback(client):
    contract = create_contract_helper(client)
    cid = contract["id"]

    client.post(f"/api/contracts/{cid}/create-hold-order")
    client.post(f"/api/contracts/{cid}/confirm-authorization", json={"paypal_order_id": "MOCK-ORDER-TEST"})

    exec_res = client.post(f"/api/contracts/{cid}/execute")
    assert exec_res.status_code == 200
    summary = exec_res.json()["summary"]
    assert "providers" in summary
    assert "localization" in summary["providers"]
    assert "is_fallback" in summary["providers"]["localization"]
    assert "model" in summary["providers"]["localization"]
