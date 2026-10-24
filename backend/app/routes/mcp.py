from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract, PaymentRecord
from app.schemas import MCPToolDefinition, MCPToolCallRequest, MCPToolCallResponse
from app.paypal_toolkit import PayPalAgentToolkit
from app.state_machine import ContractStateMachine, ContractState

router = APIRouter(prefix="/api/mcp", tags=["mcp_tools"])

@router.get("/tools", response_model=List[MCPToolDefinition])
def list_mcp_tools():
    """
    Returns the official PayPal Agent Toolkit tools exposed via Model Context Protocol (MCP).
    """
    tools = PayPalAgentToolkit.list_tools()
    return [
        MCPToolDefinition(
            name=t["name"],
            description=t["description"],
            parameters=t["parameters"]
        )
        for t in tools
    ]

@router.post("/tools/call", response_model=MCPToolCallResponse)
async def call_mcp_tool(req: MCPToolCallRequest, db: Session = Depends(get_db)):
    """
    Executes a tool call using the official PayPal Agent Toolkit integration.
    Logs execution, validates schema, and updates contract state machine if applicable.
    Capture authority is strictly rejected.
    """
    contract = None
    if req.contract_id:
        contract = db.query(Contract).filter(Contract.id == req.contract_id).first()

    # Pass contract_id so tool creates order bound to contract
    tool_res = await PayPalAgentToolkit.call_tool(
        tool_name=req.tool_name,
        arguments=req.arguments,
        contract_id=req.contract_id
    )

    # If associated with a contract and tool was create_order or authorize_order, sync DB payment record
    if contract and tool_res["status"] == "SUCCESS":
        result_data = tool_res["result"]
        if req.tool_name == "paypal_create_order":
            order_id = result_data["order_id"]
            # Check or create payment record
            payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
            if not payment:
                payment = PaymentRecord(
                    contract_id=contract.id,
                    provider="paypal",
                    paypal_order_id=order_id,
                    amount=result_data["amount"],
                    currency=result_data["currency"],
                    status="CREATED",
                    is_mock=tool_res["is_mock"]
                )
                db.add(payment)
            else:
                payment.paypal_order_id = order_id
                payment.status = "CREATED"
            
            # Transition contract to HOLD_PENDING if in DRAFT
            if contract.status == ContractState.DRAFT:
                ContractStateMachine.transition(
                    db, contract, ContractState.HOLD_PENDING,
                    actor="paypal_agent_toolkit",
                    context={"order_id": order_id, "correlation_id": tool_res["correlation_id"]}
                )
            db.commit()

        elif req.tool_name == "paypal_authorize_order":
            auth_id = result_data["authorization_id"]
            payment = db.query(PaymentRecord).filter(PaymentRecord.contract_id == contract.id).first()
            if payment:
                payment.paypal_authorization_id = auth_id
                payment.status = "AUTHORIZED"
                if contract.status == ContractState.HOLD_PENDING:
                    ContractStateMachine.transition(
                        db, contract, ContractState.AUTHORIZED,
                        actor="paypal_agent_toolkit",
                        context={"authorization_id": auth_id, "correlation_id": tool_res["correlation_id"]}
                    )
                db.commit()

        # Audit event for MCP tool call
        ContractStateMachine.record_audit(
            db,
            contract_id=contract.id,
            event_type="MCP_TOOL_CALLED",
            actor="buyer_agent",
            payload_dict={
                "tool_name": req.tool_name,
                "correlation_id": tool_res["correlation_id"],
                "status": tool_res["status"],
                "is_mock": tool_res["is_mock"]
            }
        )
        db.commit()

    return MCPToolCallResponse(
        tool_name=tool_res["tool_name"],
        status=tool_res["status"],
        result=tool_res["result"],
        is_mock=tool_res["is_mock"],
        correlation_id=tool_res["correlation_id"],
        error=tool_res["error"]
    )
