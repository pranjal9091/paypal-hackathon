import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Contract, PaymentRecord, AuditEvent, utc_now

class StateMachineError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ContractState:
    DRAFT = "DRAFT"
    READY_FOR_EXECUTION = "READY_FOR_EXECUTION"
    EXECUTING = "EXECUTING"
    VERIFIED_PASSED = "VERIFIED_PASSED"
    VERIFIED_FAILED = "VERIFIED_FAILED"
    HOLD_PENDING = "HOLD_PENDING"
    AUTHORIZED = "AUTHORIZED"
    AWAITING_BUYER_APPROVAL = "AWAITING_BUYER_APPROVAL"
    PAID = "PAID"
    VOIDED = "VOIDED"
    CANCELLED = "CANCELLED"

class ContractStateMachine:
    """
    Authoritative Server-Side State Machine for Outcome Exchange Contracts.
    Guarantees that financial state transitions strictly adhere to verified deliverables
    and explicit human approval gates.
    """

    ALLOWED_TRANSITIONS = {
        ContractState.DRAFT: [ContractState.READY_FOR_EXECUTION, ContractState.HOLD_PENDING, ContractState.CANCELLED],
        ContractState.HOLD_PENDING: [ContractState.AUTHORIZED, ContractState.CANCELLED],
        ContractState.AUTHORIZED: [ContractState.EXECUTING, ContractState.AWAITING_BUYER_APPROVAL, ContractState.VOIDED],
        ContractState.READY_FOR_EXECUTION: [ContractState.EXECUTING, ContractState.CANCELLED],
        ContractState.EXECUTING: [ContractState.VERIFIED_PASSED, ContractState.VERIFIED_FAILED, ContractState.CANCELLED],
        ContractState.VERIFIED_PASSED: [ContractState.AWAITING_BUYER_APPROVAL, ContractState.EXECUTING, ContractState.VOIDED],
        ContractState.VERIFIED_FAILED: [ContractState.EXECUTING, ContractState.VOIDED, ContractState.CANCELLED],
        ContractState.AWAITING_BUYER_APPROVAL: [ContractState.PAID, ContractState.EXECUTING, ContractState.VOIDED, ContractState.CANCELLED],
        ContractState.PAID: [], # Terminal success
        ContractState.VOIDED: [], # Terminal refund/cancellation
        ContractState.CANCELLED: [], # Terminal abort
    }

    @staticmethod
    def record_audit(db: Session, contract_id: str, event_type: str, actor: str, payload_dict: dict):
        event = AuditEvent(
            contract_id=contract_id,
            event_type=event_type,
            actor=actor,
            payload=json.dumps(payload_dict)
        )
        db.add(event)

    @classmethod
    def transition(cls, db: Session, contract: Contract, target_state: str, actor: str = "system", context: Optional[dict] = None) -> Contract:
        current_state = contract.status
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, [])

        if target_state not in allowed:
            raise StateMachineError(
                f"Illegal state transition from '{current_state}' to '{target_state}'. Allowed transitions: {allowed}"
            )

        # Enforce prerequisite invariants for critical financial states
        if target_state == ContractState.AWAITING_BUYER_APPROVAL:
            # Must have passed mandatory verification AND must have an active authorization hold
            mandatory_findings = [f for f in contract.findings if f.is_mandatory]
            if not mandatory_findings or not all(f.passed for f in mandatory_findings):
                raise StateMachineError(
                    "Cannot transition to AWAITING_BUYER_APPROVAL: verification criteria have not all passed."
                )
            if not contract.payment or contract.payment.status != "AUTHORIZED":
                raise StateMachineError(
                    "Cannot transition to AWAITING_BUYER_APPROVAL: no active authorization hold found."
                )

        if target_state == ContractState.PAID:
            if current_state != ContractState.AWAITING_BUYER_APPROVAL:
                raise StateMachineError(
                    "Cannot capture payment: contract must be in AWAITING_BUYER_APPROVAL state."
                )
            if not contract.payment or contract.payment.status not in ["AUTHORIZED", "CAPTURED"]:
                raise StateMachineError(
                    "Cannot capture payment: payment record is not in AUTHORIZED or CAPTURED state."
                )

        old_state = contract.status
        contract.status = target_state
        contract.updated_at = utc_now()

        payload = {
            "from_state": old_state,
            "to_state": target_state,
            **(context or {})
        }
        cls.record_audit(db, contract.id, f"STATE_TRANSITION_{target_state}", actor, payload)
        db.commit()
        db.refresh(contract)
        return contract
