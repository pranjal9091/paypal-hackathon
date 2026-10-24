from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ContractCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    budget_amount: str = Field(default="40.00")
    currency: str = Field(default="USD", max_length=8)
    source_strings: Dict[str, str]

class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    budget_amount: str
    currency: str
    status: str
    source_payload: str
    created_at: datetime
    updated_at: datetime

class DeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_id: str
    filename: str
    content: str
    format: str
    created_at: datetime

class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    criterion_name: str
    passed: bool
    details: str
    created_at: datetime

class VerificationReportResponse(BaseModel):
    contract_id: str
    status: str
    passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    findings: List[FindingResponse]
    deliverables: List[DeliverableResponse]

class PaymentRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_id: str
    provider: str
    paypal_order_id: Optional[str] = None
    paypal_authorization_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    amount: str
    currency: str
    status: str
    is_mock: bool
    created_at: datetime
    updated_at: datetime

class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_id: str
    event_type: str
    actor: str
    payload: str
    created_at: datetime

class CaptureRequest(BaseModel):
    buyer_approved: bool = Field(..., description="Explicit buyer authorization flag")

class AuthorizeOrderRequest(BaseModel):
    paypal_order_id: str

class AuditReceiptResponse(BaseModel):
    contract: ContractResponse
    payment: Optional[PaymentRecordResponse] = None
    verification: Optional[VerificationReportResponse] = None
    audit_events: List[AuditEventResponse]
