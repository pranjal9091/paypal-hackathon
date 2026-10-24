import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract, PaymentRecord, VerificationFinding, AuditEvent
from app.schemas import (
    BuyerConsultationRequest,
    ContractProposalResponse,
    BuyerConfirmRequest,
    ContractResponse,
    AgentReasoningTimelineResponse
)
from app.agents.buyer_agent import BuyerAgent
from app.state_machine import ContractStateMachine, ContractState

router = APIRouter(prefix="/api/buyer", tags=["buyer_agent"])

@router.post("/propose", response_model=ContractProposalResponse)
async def formulate_contract_proposal(req: BuyerConsultationRequest):
    """
    Buyer Agent analyzes a natural-language procurement request and produces
    a structured contract proposal with explicit acceptance criteria and rationale.
    """
    proposal = await BuyerAgent.formulate_proposal(
        user_prompt=req.prompt,
        simulate_missing_info=req.simulate_missing_info,
        simulate_contradiction=req.simulate_contradiction,
        force_fallback=req.force_fallback
    )
    return proposal

@router.post("/confirm", response_model=ContractResponse)
def confirm_contract_proposal(req: BuyerConfirmRequest, db: Session = Depends(get_db)):
    """
    Human-controlled Gate 1: Buyer explicitly approves the proposed contract terms.
    The authoritative backend initializes the contract in DRAFT state.
    Amounts, currency, and source strings are persisted under trusted server control.
    """
    amt = float(req.budget_amount)
    if amt <= 0:
        raise HTTPException(status_code=400, detail="Contract budget must be greater than zero.")

    contract = Contract(
        title=req.title,
        description=req.description,
        budget_amount=f"{amt:.2f}",
        currency=req.currency.upper(),
        status=ContractState.DRAFT,
        source_payload=json.dumps(req.source_strings)
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    ContractStateMachine.record_audit(
        db,
        contract_id=contract.id,
        event_type="BUYER_CONFIRMED_TERMS",
        actor="buyer",
        payload_dict={
            "action": "contract_confirmed_by_buyer",
            "title": contract.title,
            "budget": f"{contract.budget_amount} {contract.currency}",
            "keys_count": len(req.source_strings)
        }
    )
    db.commit()

    return ContractResponse.model_validate(contract)

@router.get("/contracts/{contract_id}/reasoning", response_model=AgentReasoningTimelineResponse)
def get_agent_reasoning_timeline(contract_id: str, db: Session = Depends(get_db)):
    """
    Produces a transparent, auditable timeline of Buyer Agent reasoning,
    tool calls, verification findings, and current payment release status.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    audit_events = db.query(AuditEvent).filter(AuditEvent.contract_id == contract.id).order_by(AuditEvent.created_at.asc()).all()
    findings = db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).all()
    payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()

    has_active_hold = payment is not None and payment.status in ["AUTHORIZED", "CAPTURED"]

    findings_dicts = [
        {
            "criterion_name": f.criterion_name,
            "passed": f.passed,
            "details": f.details,
            "evaluator": f.evaluator,
            "is_mandatory": f.is_mandatory
        }
        for f in findings
    ]

    gate_info = BuyerAgent.explain_gate_decision(
        contract_status=contract.status,
        findings=findings_dicts,
        has_active_hold=has_active_hold
    )

    timeline_items = []
    for ev in audit_events:
        payload_data = {}
        try:
            payload_data = json.loads(ev.payload)
        except Exception:
            payload_data = {"raw": ev.payload}

        timeline_items.append({
            "event_type": ev.event_type,
            "actor": ev.actor,
            "timestamp": ev.created_at.isoformat(),
            "details": payload_data
        })

    return AgentReasoningTimelineResponse(
        contract_id=contract.id,
        current_status=contract.status,
        reasoning_summary=gate_info["explanation"],
        timeline=timeline_items
    )
