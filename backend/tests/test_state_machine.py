import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import Contract, PaymentRecord, VerificationFinding
from app.state_machine import ContractStateMachine, ContractState, StateMachineError

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_illegal_state_transition_from_draft():
    db = TestingSessionLocal()
    contract = Contract(
        title="Test Contract",
        description="Test",
        budget_amount="40.00",
        currency="USD",
        status=ContractState.DRAFT,
        source_payload="{}"
    )
    db.add(contract)
    db.commit()

    # DRAFT directly to PAID is strictly illegal
    with pytest.raises(StateMachineError) as exc_info:
        ContractStateMachine.transition(db, contract, ContractState.PAID)
    assert "Illegal state transition" in exc_info.value.message

def test_transition_to_awaiting_approval_requires_all_findings_passed():
    db = TestingSessionLocal()
    contract = Contract(
        title="Test Contract",
        description="Test",
        budget_amount="40.00",
        currency="USD",
        status=ContractState.AUTHORIZED,
        source_payload="{}"
    )
    db.add(contract)
    db.commit()

    # Add Payment in AUTHORIZED status
    payment = PaymentRecord(
        contract_id=contract.id,
        provider="paypal",
        amount="40.00",
        currency="USD",
        status="AUTHORIZED"
    )
    db.add(payment)

    # Add a failed finding
    finding = VerificationFinding(
        contract_id=contract.id,
        criterion_name="required_keys",
        passed=False,
        details="Key missing"
    )
    db.add(finding)
    db.commit()
    db.refresh(contract)

    # Transition to AWAITING_BUYER_APPROVAL must raise error because a finding failed
    with pytest.raises(StateMachineError) as exc_info:
        ContractStateMachine.transition(db, contract, ContractState.AWAITING_BUYER_APPROVAL)
    assert "verification criteria have not all passed" in exc_info.value.message
