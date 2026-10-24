import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    budget_amount = Column(String(32), nullable=False, default="40.00")
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(64), nullable=False, default="DRAFT")
    source_payload = Column(Text, nullable=False) # JSON encoded input strings
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    deliverables = relationship("Deliverable", back_populates="contract", cascade="all, delete-orphan")
    findings = relationship("VerificationFinding", back_populates="contract", cascade="all, delete-orphan")
    payment = relationship("PaymentRecord", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="contract", cascade="all, delete-orphan")

class Deliverable(Base):
    __tablename__ = "deliverables"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    format = Column(String(32), nullable=False, default="json")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    contract = relationship("Contract", back_populates="deliverables")

class VerificationFinding(Base):
    __tablename__ = "verification_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=False)
    deliverable_id = Column(String(36), ForeignKey("deliverables.id"), nullable=True)
    criterion_name = Column(String(128), nullable=False)
    passed = Column(Boolean, nullable=False)
    details = Column(Text, nullable=False)
    evaluator = Column(String(32), nullable=False, default="deterministic") # "deterministic" or "qa_agent"
    is_mandatory = Column(Boolean, nullable=False, default=True) # deterministic checks are mandatory for payment release
    created_at = Column(DateTime, default=utc_now, nullable=False)

    contract = relationship("Contract", back_populates="findings")

class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=False, unique=True)
    provider = Column(String(32), nullable=False, default="paypal")
    paypal_order_id = Column(String(128), nullable=True, index=True)
    paypal_authorization_id = Column(String(128), nullable=True, index=True)
    paypal_capture_id = Column(String(128), nullable=True, index=True)
    amount = Column(String(32), nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    status = Column(String(64), nullable=False, default="CREATED")
    # Statuses: CREATED, AUTHORIZED (Hold), CAPTURED, VOIDED, FAILED
    is_mock = Column(Boolean, nullable=False, default=False)
    approval_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    contract = relationship("Contract", back_populates="payment")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False, default="system")
    payload = Column(Text, nullable=False) # JSON formatted event data
    created_at = Column(DateTime, default=utc_now, nullable=False)

    contract = relationship("Contract", back_populates="audit_events")
