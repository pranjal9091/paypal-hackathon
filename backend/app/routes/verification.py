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
    Executes independent multi-artifact verification on contract deliverables.
    Validates complete bundle (JSON translations + Markdown landing page + QA review).
    Fails closed: If any mandatory deterministic check fails, payment capture is strictly blocked.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    deliverables = db.query(Deliverable).filter(Deliverable.contract_id == contract.id).all()

    # Clear previous findings for this contract
    db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).delete()

    if not deliverables:
        finding = VerificationFinding(
            contract_id=contract.id,
            criterion_name="bundle_deliverable_completeness",
            passed=False,
            details="No deliverable artifacts found for contract. Verification blocked.",
            evaluator="deterministic",
            is_mandatory=True
        )
        db.add(finding)
        db.commit()
        ContractStateMachine.transition(
            db, contract, ContractState.VERIFIED_FAILED,
            actor="verifier",
            context={"reason": "Missing deliverable bundle"}
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

    deliverables_map = {d.filename: d.content for d in deliverables}
    deliverables_id_map = {d.filename: d.id for d in deliverables}
    source_strings = json.loads(contract.source_payload)

    # Execute full bundle verification
    passed, results = DeterministicVerifier.verify_bundle(source_strings, deliverables_map)

    findings_records = []
    for r in results:
        deliv_id = deliverables_id_map.get(r.deliverable_filename) if r.deliverable_filename else None
        f = VerificationFinding(
            contract_id=contract.id,
            deliverable_id=deliv_id,
            criterion_name=r.criterion_name,
            passed=r.passed,
            details=r.details,
            evaluator=r.evaluator,
            is_mandatory=r.is_mandatory
        )
        db.add(f)
        findings_records.append(f)
    db.commit()

    target_state = ContractState.VERIFIED_PASSED if passed else ContractState.VERIFIED_FAILED

    # Transition to verified status if in executable states
    if contract.status in [ContractState.EXECUTING, ContractState.DRAFT, ContractState.AUTHORIZED, ContractState.READY_FOR_EXECUTION, ContractState.VERIFIED_FAILED, ContractState.VERIFIED_PASSED]:
        ContractStateMachine.transition(
            db, contract, target_state,
            actor="verifier",
            context={"all_mandatory_checks_passed": passed, "checks_count": len(results)}
        )

    # If verification passed AND an authorization hold is already active, advance to AWAITING_BUYER_APPROVAL
    if passed and contract.payment and contract.payment.status == "AUTHORIZED":
        ContractStateMachine.transition(
            db, contract, ContractState.AWAITING_BUYER_APPROVAL,
            actor="system",
            context={"reason": "Multi-artifact bundle verified and authorization hold ready"}
        )

    db.refresh(contract)

    finding_responses = [FindingResponse.model_validate(f) for f in findings_records]
    deliverable_responses = [DeliverableResponse.model_validate(d) for d in deliverables]

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

    # Mandatory checks dictate final passed boolean
    mandatory_findings = [f for f in findings if f.is_mandatory]
    passed = len(mandatory_findings) > 0 and all(f.passed for f in mandatory_findings)

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
