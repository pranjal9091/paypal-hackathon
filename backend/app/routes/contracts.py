import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract, Deliverable, AuditEvent
from app.schemas import ContractCreate, ContractResponse, DeliverableResponse
from app.state_machine import ContractStateMachine, ContractState, StateMachineError
from app.agents.localization_agent import LocalizationAgent

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

# Canonical Spanish Launch Kit UI strings
SAMPLE_LAUNCH_KIT_STRINGS = {
    "app_title": "TidyLedger — Modern Cloud Accounting",
    "login_button": "Log in to your account",
    "signup_prompt": "Don't have an account? Sign up here.",
    "welcome_message": "Welcome back, {user}! Your financial dashboard is up to date.",
    "password_reset_notice": "A password recovery link has been sent to {email}.",
    "invoice_summary": "You have {count} pending invoices awaiting approval for {company}.",
    "cta_start_free": "Start your free 14-day trial",
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

@router.post("/{contract_id}/execute", response_model=DeliverableResponse)
async def execute_task(
    contract_id: str,
    simulate_missing_key: bool = Query(False, description="Simulate an agent failing to produce a required key"),
    simulate_broken_placeholder: bool = Query(False, description="Simulate an agent corrupting a placeholder"),
    simulate_prompt_injection: bool = Query(False, description="Simulate prompt injection in agent output"),
    db: Session = Depends(get_db)
):
    """
    Executes the task using the Localization Agent, generating the es_translations.json artifact.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Transition to EXECUTING if currently in DRAFT, READY_FOR_EXECUTION, or AUTHORIZED
    if contract.status in [ContractState.DRAFT, ContractState.READY_FOR_EXECUTION, ContractState.AUTHORIZED]:
        ContractStateMachine.transition(db, contract, ContractState.EXECUTING, actor="system", context={"stage": "localization_agent_start"})

    source_strings = json.loads(contract.source_payload)

    # Run agent
    agent_output = await LocalizationAgent.execute(
        source_strings=source_strings,
        simulate_missing_key=simulate_missing_key,
        simulate_broken_placeholder=simulate_broken_placeholder,
        simulate_prompt_injection=simulate_prompt_injection
    )

    # Clean existing deliverables for this contract
    db.query(Deliverable).filter(Deliverable.contract_id == contract.id).delete()

    deliverable = Deliverable(
        contract_id=contract.id,
        filename=agent_output["filename"],
        content=agent_output["content"],
        format="json"
    )
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    ContractStateMachine.record_audit(
        db,
        contract.id,
        "DELIVERABLE_GENERATED",
        "localization_agent",
        {
            "filename": deliverable.filename,
            "provider": agent_output.get("provider"),
            "is_fallback": agent_output.get("is_fallback")
        }
    )
    db.commit()
    return deliverable
