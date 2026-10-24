import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract, Deliverable, VerificationFinding
from app.schemas import VerificationReportResponse, FindingResponse, DeliverableResponse
from app.state_machine import ContractStateMachine, ContractState
from app.verifier.deterministic_verifier import DeterministicVerifier

router = APIRouter(prefix="/api/contracts", tags=["verification"])

@router.post("/{contract_id}/verify", response_model=VerificationReportResponse)
def run_verification(contract_id: str, db: Session = Depends(get_db)):
    """
    Executes deterministic verification on contract deliverables.
    Enforces that incomplete or invalid artifacts are blocked from payment.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    deliverable = db.query(Deliverable).filter(Deliverable.contract_id == contract.id).first()

    # Clear previous findings
    db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).delete()

    if not deliverable:
        finding = VerificationFinding(
            contract_id=contract.id,
            criterion_name="deliverable_existence",
            passed=False,
            details="No deliverable artifact found for contract. Verification blocked."
        )
        db.add(finding)
        db.commit()
        ContractStateMachine.transition(
            db, contract, ContractState.VERIFIED_FAILED,
            actor="verifier",
            context={"reason": "Missing deliverable file"}
        )
        findings = [FindingResponse.model_validate(finding)]
        return VerificationReportResponse(
            contract_id=contract.id,
            status=ContractState.VERIFIED_FAILED,
            passed=False,
            total_checks=1,
            passed_checks=0,
            failed_checks=1,
            findings=findings,
            deliverables=[]
        )

    source_strings = json.loads(contract.source_payload)
    passed, results = DeterministicVerifier.verify(source_strings, deliverable.content)

    findings_records = []
    for r in results:
        f = VerificationFinding(
            contract_id=contract.id,
            deliverable_id=deliverable.id,
            criterion_name=r.criterion_name,
            passed=r.passed,
            details=r.details
        )
        db.add(f)
        findings_records.append(f)
    db.commit()

    target_state = ContractState.VERIFIED_PASSED if passed else ContractState.VERIFIED_FAILED

    # Transition to verified status
    if contract.status in [ContractState.EXECUTING, ContractState.DRAFT, ContractState.AUTHORIZED, ContractState.READY_FOR_EXECUTION]:
        ContractStateMachine.transition(
            db, contract, target_state,
            actor="verifier",
            context={"all_checks_passed": passed, "checks_count": len(results)}
        )

    # If verification passed AND an authorization hold is already active, advance to AWAITING_BUYER_APPROVAL
    if passed and contract.payment and contract.payment.status == "AUTHORIZED":
        ContractStateMachine.transition(
            db, contract, ContractState.AWAITING_BUYER_APPROVAL,
            actor="system",
            context={"reason": "Deliverables verified and authorization hold ready"}
        )

    db.refresh(contract)

    finding_responses = [FindingResponse.model_validate(f) for f in findings_records]
    deliverable_responses = [DeliverableResponse.model_validate(deliverable)]

    return VerificationReportResponse(
        contract_id=contract.id,
        status=contract.status,
        passed=passed,
        total_checks=len(results),
        passed_checks=sum(1 for r in results if r.passed),
        failed_checks=sum(1 for r in results if not r.passed),
        findings=finding_responses,
        deliverables=deliverable_responses
    )

@router.get("/{contract_id}/verification-report", response_model=VerificationReportResponse)
def get_verification_report(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    findings = db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).all()
    deliverables = db.query(Deliverable).filter(Deliverable.contract_id == contract.id).all()

    passed = len(findings) > 0 and all(f.passed for f in findings)
    return VerificationReportResponse(
        contract_id=contract.id,
        status=contract.status,
        passed=passed,
        total_checks=len(findings),
        passed_checks=sum(1 for f in findings if f.passed),
        failed_checks=sum(1 for f in findings if not f.passed),
        findings=[FindingResponse.model_validate(f) for f in findings],
        deliverables=[DeliverableResponse.model_validate(d) for d in deliverables]
    )
