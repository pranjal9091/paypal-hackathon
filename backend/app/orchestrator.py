import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Contract, Deliverable, VerificationFinding
from app.state_machine import ContractStateMachine, ContractState
from app.agents.localization_agent import LocalizationAgent
from app.agents.content_agent import ContentAgent
from app.agents.qa_agent import QAAgent

class MultiAgentOrchestrator:
    """
    Coordinates execution of the 3 specialized agents:
    1. Localization Agent -> es_translations.json
    2. Content Agent      -> landing_page_es.md
    3. QA Agent           -> qa_report.json
    """

    @classmethod
    async def execute_workflow(
        cls,
        db: Session,
        contract: Contract,
        simulate_missing_key: bool = False,
        simulate_broken_placeholder: bool = False,
        simulate_missing_section: bool = False,
        simulate_word_count_violation: bool = False,
        simulate_unsupported_claim: bool = False,
        simulate_prompt_injection: bool = False,
        simulate_qa_failure: bool = False,
        force_fallback: bool = False
    ) -> Dict[str, Any]:
        # Advance contract state to EXECUTING if not already
        if contract.status in [
            ContractState.DRAFT,
            ContractState.READY_FOR_EXECUTION,
            ContractState.AUTHORIZED,
            ContractState.VERIFIED_FAILED,
            ContractState.VERIFIED_PASSED,
            ContractState.AWAITING_BUYER_APPROVAL
        ]:
            ContractStateMachine.transition(
                db, contract, ContractState.EXECUTING,
                actor="orchestrator",
                context={"action": "multi_agent_execution_start"}
            )

        source_strings = json.loads(contract.source_payload)

        # 1. Localization Agent
        loc_res = await LocalizationAgent.execute(
            source_strings=source_strings,
            simulate_missing_key=simulate_missing_key,
            simulate_broken_placeholder=simulate_broken_placeholder,
            simulate_prompt_injection=simulate_prompt_injection,
            force_fallback=force_fallback
        )

        # 2. Content Agent
        content_res = await ContentAgent.execute(
            contract_title=contract.title,
            contract_desc=contract.description,
            simulate_missing_section=simulate_missing_section,
            simulate_word_count_violation=simulate_word_count_violation,
            simulate_unsupported_claim=simulate_unsupported_claim,
            force_fallback=force_fallback
        )

        # 3. QA Agent
        qa_res = await QAAgent.review(
            translations_content=loc_res["content"],
            landing_content=content_res["content"],
            simulate_qa_failure=simulate_qa_failure,
            force_fallback=force_fallback
        )

        # Delete previous verification findings and deliverables to avoid foreign key conflicts
        db.query(VerificationFinding).filter(VerificationFinding.contract_id == contract.id).delete()
        db.query(Deliverable).filter(Deliverable.contract_id == contract.id).delete()

        deliv_loc = Deliverable(
            contract_id=contract.id,
            filename=loc_res["filename"],
            content=loc_res["content"],
            format="json"
        )
        deliv_content = Deliverable(
            contract_id=contract.id,
            filename=content_res["filename"],
            content=content_res["content"],
            format="markdown"
        )
        deliv_qa = Deliverable(
            contract_id=contract.id,
            filename=qa_res["filename"],
            content=qa_res["content"],
            format="json"
        )

        db.add_all([deliv_loc, deliv_content, deliv_qa])
        db.commit()
        db.refresh(deliv_loc)
        db.refresh(deliv_content)
        db.refresh(deliv_qa)

        execution_summary = {
            "agents_executed": ["localization_agent", "content_agent", "qa_agent"],
            "artifacts_generated": [
                deliv_loc.filename,
                deliv_content.filename,
                deliv_qa.filename
            ],
            "providers": {
                "localization": {"provider": loc_res["provider"], "mode": loc_res["mode"]},
                "content": {"provider": content_res["provider"], "mode": content_res["mode"]},
                "qa": {"provider": qa_res["provider"], "mode": qa_res["mode"]},
            }
        }

        ContractStateMachine.record_audit(
            db,
            contract.id,
            "MULTI_AGENT_EXECUTION_COMPLETED",
            "orchestrator",
            execution_summary
        )
        db.commit()

        return {
            "summary": execution_summary,
            "deliverables": [deliv_loc, deliv_content, deliv_qa]
        }
