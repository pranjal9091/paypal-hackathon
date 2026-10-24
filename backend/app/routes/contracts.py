import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract, Deliverable
from app.schemas import ContractCreate, ContractResponse, DeliverableResponse
from app.state_machine import ContractStateMachine, ContractState
from app.orchestrator import MultiAgentOrchestrator

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

SAMPLE_LAUNCH_KIT_STRINGS = {
    "app_title": "TidyLedger — Modern Cloud Accounting",
    "login_button": "Log in to your account",
    "signup_prompt": "Don't have an account? Sign up here.",
    "welcome_message": "Welcome back, {user}! Your financial dashboard is up to date.",
    "password_reset_notice": "A password recovery link has been sent to {email}.",
    "invoice_summary": "You have {count} pending invoices awaiting approval for {company}.",
    "cta_start_free": "Start your free 14-day trial"
}

@router.post("", response_model=ContractResponse)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    """
    Creates an Outcome Contract with structured acceptance criteria and budget.
    """
    source_json = json.dumps(payload.source_strings or SAMPLE_LAUNCH_KIT_STRINGS)
    contract = Contract(
        title=payload.title,
        description=payload.description,
        budget_amount=payload.budget_amount or "40.00",
        currency=payload.currency or "USD",
        status=ContractState.DRAFT,
        source_payload=source_json
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    ContractStateMachine.record_audit(
        db,
        contract.id,
        "CONTRACT_CREATED",
        "buyer",
        {
            "title": contract.title,
            "budget": f"{contract.budget_amount} {contract.currency}",
            "string_count": len(payload.source_strings or SAMPLE_LAUNCH_KIT_STRINGS)
        }
    )
    db.commit()
    return contract

@router.get("", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).order_by(Contract.created_at.desc()).all()

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.get("/{contract_id}/deliverables", response_model=List[DeliverableResponse])
def list_deliverables(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return db.query(Deliverable).filter(Deliverable.contract_id == contract.id).all()

@router.post("/{contract_id}/execute")
async def execute_task(
    contract_id: str,
    simulate_missing_key: bool = Query(False, description="Simulate Localization Agent failing a required key"),
    simulate_broken_placeholder: bool = Query(False, description="Simulate Localization Agent corrupting a placeholder"),
    simulate_missing_section: bool = Query(False, description="Simulate Content Agent omitting a required section"),
    simulate_word_count_violation: bool = Query(False, description="Simulate Content Agent word-count violation"),
    simulate_unsupported_claim: bool = Query(False, description="Simulate Content Agent adding unsupported claim"),
    simulate_prompt_injection: bool = Query(False, description="Simulate prompt injection in agent input"),
    simulate_qa_failure: bool = Query(False, description="Simulate QA Agent failing quality review"),
    force_fallback: bool = Query(False, description="Force offline deterministic fallback"),
    db: Session = Depends(get_db)
):
    """
    Executes the multi-agent workflow:
    1. Localization Agent -> es_translations.json
    2. Content Agent      -> landing_page_es.md
    3. QA Agent           -> qa_report.json
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    res = await MultiAgentOrchestrator.execute_workflow(
        db=db,
        contract=contract,
        simulate_missing_key=simulate_missing_key,
        simulate_broken_placeholder=simulate_broken_placeholder,
        simulate_missing_section=simulate_missing_section,
        simulate_word_count_violation=simulate_word_count_violation,
        simulate_unsupported_claim=simulate_unsupported_claim,
        simulate_prompt_injection=simulate_prompt_injection,
        simulate_qa_failure=simulate_qa_failure,
        force_fallback=force_fallback
    )

    deliverable_responses = [DeliverableResponse.model_validate(d) for d in res["deliverables"]]
    # Return first deliverable for backwards compatibility with single deliverable schema, plus summary
    first_deliv = deliverable_responses[0]
    return {
        "id": first_deliv.id,
        "contract_id": first_deliv.contract_id,
        "filename": first_deliv.filename,
        "content": first_deliv.content,
        "format": first_deliv.format,
        "created_at": first_deliv.created_at,
        "deliverables": deliverable_responses,
        "summary": res["summary"]
    }
