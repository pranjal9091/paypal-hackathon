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
    evaluator: str = "deterministic"
    is_mandatory: bool = True
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
    approval_url: Optional[str] = None
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

# Milestone 3: Buyer Agent & MCP Schemas
class BuyerConsultationRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="Natural language outcome request from buyer")
    simulate_missing_info: bool = Field(default=False, description="Simulate incomplete input requiring clarification")
    simulate_contradiction: bool = Field(default=False, description="Simulate contradictory request")
    force_fallback: bool = Field(default=False, description="Force deterministic rule-based proposal")

class ContractProposalResponse(BaseModel):
    title: str
    description: str
    budget_amount: str
    currency: str
    requested_deliverables: List[str]
    acceptance_criteria: List[Dict[str, str]]
    acceptance_criteria_rationale: str
    clarification_needed: Optional[str] = None
    is_valid: bool
    source_strings: Dict[str, str]

class BuyerConfirmRequest(BaseModel):
    title: str
    description: str
    budget_amount: str
    currency: str
    source_strings: Dict[str, str]

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    contract_id: Optional[str] = None

class MCPToolCallResponse(BaseModel):
    tool_name: str
    status: str  # "SUCCESS" or "ERROR"
    result: Optional[Any] = None
    is_mock: bool
    correlation_id: str
    error: Optional[str] = None

class AgentReasoningTimelineResponse(BaseModel):
    contract_id: str
    current_status: str
    reasoning_summary: str
    timeline: List[Dict[str, Any]]

