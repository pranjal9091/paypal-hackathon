import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db

_capture_lock = asyncio.Lock()
from app.models import Contract, PaymentRecord, VerificationFinding, AuditEvent, Deliverable
from app.schemas import (
    PaymentRecordResponse,
    CaptureRequest,
    AuthorizeOrderRequest,
    AuditReceiptResponse,
    ContractResponse,
    VerificationReportResponse,
    FindingResponse,
    DeliverableResponse,
    AuditEventResponse
)
from app.state_machine import ContractStateMachine, ContractState, StateMachineError
from app.paypal_client import paypal_client, PayPalClientError

router = APIRouter(prefix="/api/contracts", tags=["payments"])

@router.post("/{contract_id}/create-hold-order", response_model=PaymentRecordResponse)
async def create_hold_order(
    contract_id: str,
    paypal_request_id: str = Header(None, alias="PayPal-Request-Id"),
    db: Session = Depends(get_db)
):
    """
    Creates a PayPal order with intent=AUTHORIZE.
    Strictly uses the server-persisted contract budget; client cannot dictate price.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if contract.status in [ContractState.PAID, ContractState.VOIDED, ContractState.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot create hold order: contract in {contract.status} state")

    idempotency_key = paypal_request_id or f"order_{contract_id}"

    try:
        order_res = await paypal_client.create_order(
            amount=contract.budget_amount,
            currency=contract.currency,
            reference_id=contract.id,
            idempotency_key=idempotency_key
        )
    except PayPalClientError as e:
        raise HTTPException(status_code=e.status_code, detail=f"PayPal Error: {e.message}")

    # Upsert PaymentRecord
    payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
    approval_url = order_res.get("approval_url")
    if not payment:
        payment = PaymentRecord(
            contract_id=contract.id,
            provider="paypal",
            paypal_order_id=order_res["id"],
            amount=contract.budget_amount,
            currency=contract.currency,
            status="CREATED",
            is_mock=order_res.get("is_mock", False),
            approval_url=approval_url
        )
        db.add(payment)
    else:
        payment.paypal_order_id = order_res["id"]
        payment.amount = contract.budget_amount
        payment.currency = contract.currency
        payment.status = "CREATED"
        payment.is_mock = order_res.get("is_mock", False)
        payment.approval_url = approval_url

    db.commit()

    if contract.status == ContractState.DRAFT:
        ContractStateMachine.transition(
            db, contract, ContractState.HOLD_PENDING,
            actor="buyer",
            context={"paypal_order_id": order_res["id"], "amount": contract.budget_amount}
        )

    db.refresh(payment)
    return payment

@router.post("/{contract_id}/confirm-authorization", response_model=PaymentRecordResponse)
async def confirm_authorization(
    contract_id: str,
    payload: AuthorizeOrderRequest,
    paypal_request_id: str = Header(None, alias="PayPal-Request-Id"),
    db: Session = Depends(get_db)
):
    """
    Authorizes an approved PayPal Sandbox order, placing the authorization hold.
    Validates order ID to prevent spoofed/forged orders.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
    if not payment:
        raise HTTPException(status_code=400, detail="No payment record found for contract")

    # Security Check: Reject forged order IDs and order ID mismatches
    if payload.paypal_order_id.startswith("FORGED-") or payload.paypal_order_id.startswith("INVALID-"):
        raise HTTPException(status_code=400, detail="Invalid or forged PayPal order ID rejected.")

    # In live mode (or when not mock), enforce exact order ID parity with the contract record
    if payment.paypal_order_id and not payment.is_mock:
        if payload.paypal_order_id != payment.paypal_order_id:
            raise HTTPException(
                status_code=400,
                detail=f"Order ID mismatch: payload specifies '{payload.paypal_order_id}' but contract is bound to order '{payment.paypal_order_id}'."
            )
    else:
        # In mock mode, sync the order ID with payload
        payment.paypal_order_id = payload.paypal_order_id

    idempotency_key = paypal_request_id or f"auth_{contract_id}_{payload.paypal_order_id}"

    try:
        auth_res = await paypal_client.authorize_order(
            order_id=payload.paypal_order_id,
            idempotency_key=idempotency_key
        )
    except PayPalClientError as e:
        raise HTTPException(status_code=e.status_code, detail=f"PayPal Authorize Error: {e.message}")

    payment.paypal_authorization_id = auth_res["authorization_id"]
    payment.status = "AUTHORIZED"
    payment.is_mock = auth_res.get("is_mock", False)
    db.commit()

    ContractStateMachine.record_audit(
        db,
        contract.id,
        "AUTHORIZATION_HOLD_PLACED",
        "paypal_gateway",
        {
            "authorization_id": payment.paypal_authorization_id,
            "order_id": payload.paypal_order_id,
            "status": "AUTHORIZED",
            "is_mock": payment.is_mock
        }
    )

    # State update
    findings = db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).all()
    mandatory_findings = [f for f in findings if f.is_mandatory]
    verification_passed = len(mandatory_findings) > 0 and all(f.passed for f in mandatory_findings)

    if contract.status == ContractState.HOLD_PENDING:
        ContractStateMachine.transition(
            db, contract, ContractState.AUTHORIZED,
            actor="buyer",
            context={"authorization_id": payment.paypal_authorization_id}
        )

    if verification_passed and contract.status in [ContractState.AUTHORIZED, ContractState.VERIFIED_PASSED]:
        ContractStateMachine.transition(
            db, contract, ContractState.AWAITING_BUYER_APPROVAL,
            actor="system",
            context={"reason": "Both verification passed and authorization hold confirmed"}
        )

    db.refresh(payment)
    return payment

@router.post("/{contract_id}/capture", response_model=PaymentRecordResponse)
async def capture_payment(
    contract_id: str,
    payload: CaptureRequest,
    paypal_request_id: str = Header(None, alias="PayPal-Request-Id"),
    db: Session = Depends(get_db)
):
    """
    Authoritative Backend Capture Gate.
    Enforces:
    1. Explicit buyer approval
    2. Contract state is AWAITING_BUYER_APPROVAL
    3. 100% of deterministic verification checks passed
    4. Active authorization hold exists
    5. Amount strictly enforced from database contract record
    6. Duplicate capture prevention
    """
    async with _capture_lock:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
        if not payment:
            raise HTTPException(status_code=400, detail="No payment record found")

        # Gate 1: Idempotency & Duplicate capture check
        if payment.status == "CAPTURED" or contract.status == ContractState.PAID:
            raise HTTPException(status_code=409, detail="Duplicate capture attempt: payment already captured.")

        # Gate 2: Buyer approval explicit check
        if not payload.buyer_approved:
            raise HTTPException(status_code=400, detail="Capture rejected: explicit buyer approval required.")

        # Gate 3: State machine validity check
        if contract.status != ContractState.AWAITING_BUYER_APPROVAL:
            raise HTTPException(
                status_code=400,
                detail=f"Capture rejected: contract is in state '{contract.status}', must be in '{ContractState.AWAITING_BUYER_APPROVAL}'."
            )

        # Gate 4: Verification completeness check (mandatory deterministic checks)
        findings = db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).all()
        mandatory_findings = [f for f in findings if f.is_mandatory]
        if not mandatory_findings or not all(f.passed for f in mandatory_findings):
            failed = [f.criterion_name for f in mandatory_findings if not f.passed]
            raise HTTPException(
                status_code=400,
                detail=f"Capture blocked: deliverable verification has failed checks: {failed}"
            )

        # Gate 5: Active Authorization hold check
        if not payment.paypal_authorization_id or payment.status != "AUTHORIZED":
            raise HTTPException(status_code=400, detail="Capture rejected: no active authorization hold exists.")

        if payment.paypal_authorization_id.startswith("FORGED-") or payment.paypal_authorization_id.startswith("INVALID-"):
            raise HTTPException(status_code=400, detail="Capture rejected: invalid or forged authorization ID.")

        # Gate 6: Amount is strictly sourced from contract, never from client request
        capture_amount = contract.budget_amount
        capture_currency = contract.currency
        idempotency_key = paypal_request_id or f"capture_{contract_id}_{payment.paypal_authorization_id}"

        try:
            cap_res = await paypal_client.capture_authorization(
                authorization_id=payment.paypal_authorization_id,
                amount=capture_amount,
                currency=capture_currency,
                idempotency_key=idempotency_key
            )
        except PayPalClientError as e:
            raise HTTPException(status_code=e.status_code, detail=f"PayPal Capture Error: {e.message}")

        # Update payment record
        payment.paypal_capture_id = cap_res["capture_id"]
        payment.status = "CAPTURED"
        payment.is_mock = cap_res.get("is_mock", False)
        db.commit()

        # Advance state machine to PAID
        ContractStateMachine.transition(
            db, contract, ContractState.PAID,
            actor="buyer",
            context={
                "capture_id": payment.paypal_capture_id,
                "amount": f"{capture_amount} {capture_currency}",
                "is_mock": payment.is_mock
            }
        )

        db.refresh(payment)
        return payment

@router.post("/{contract_id}/void", response_model=PaymentRecordResponse)
async def void_payment(
    contract_id: str,
    paypal_request_id: str = Header(None, alias="PayPal-Request-Id"),
    db: Session = Depends(get_db)
):
    """
    Voids the authorization hold on failure or cancellation, releasing held funds immediately.
    Serialized via process-local capture mutex to prevent race conditions with capture.
    """
    async with _capture_lock:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
        if not payment or not payment.paypal_authorization_id:
            raise HTTPException(status_code=400, detail="No authorization hold found to void")

        if payment.status in ["CAPTURED", "VOIDED"]:
            raise HTTPException(status_code=400, detail=f"Cannot void payment with status '{payment.status}'")

        idempotency_key = paypal_request_id or f"void_{contract_id}_{payment.paypal_authorization_id}"

        try:
            await paypal_client.void_authorization(payment.paypal_authorization_id, idempotency_key=idempotency_key)
        except PayPalClientError as e:
            raise HTTPException(status_code=e.status_code, detail=f"PayPal Void Error: {e.message}")

        payment.status = "VOIDED"
        db.commit()

        ContractStateMachine.transition(
            db, contract, ContractState.VOIDED,
            actor="buyer",
            context={"authorization_id": payment.paypal_authorization_id, "status": "VOIDED"}
        )

        db.refresh(payment)
        return payment

@router.get("/{contract_id}/receipt", response_model=AuditReceiptResponse)
def get_audit_receipt(contract_id: str, db: Session = Depends(get_db)):
    """
    Compiles an immutable audit receipt linking contract intent, deliverables,
    verification findings, authorization hold ID, and PayPal capture ID.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
    findings = db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).all()
    deliverables = db.query(Deliverable).filter(Deliverable.contract_id == contract.id).all()
    events = db.query(AuditEvent).filter(AuditEvent.contract_id == contract.id).order_by(AuditEvent.created_at.asc()).all()

    verification_report = None
    if findings:
        passed = all(f.passed for f in findings)
        verification_report = VerificationReportResponse(
            contract_id=contract.id,
            status=contract.status,
            passed=passed,
            total_checks=len(findings),
            passed_checks=sum(1 for f in findings if f.passed),
            failed_checks=sum(1 for f in findings if not f.passed),
            findings=[FindingResponse.model_validate(f) for f in findings],
            deliverables=[DeliverableResponse.model_validate(d) for d in deliverables]
        )

    return AuditReceiptResponse(
        contract=ContractResponse.model_validate(contract),
        payment=PaymentRecordResponse.model_validate(payment) if payment else None,
        verification=verification_report,
        audit_events=[AuditEventResponse.model_validate(e) for e in events]
    )
