import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.llm_client import llm_client
from app.schemas import ContractProposalResponse

logger = logging.getLogger(__name__)

DEFAULT_SOURCE_STRINGS = {
    "app_title": "TidyLedger — Modern Cloud Accounting",
    "login_button": "Log in to your account",
    "signup_prompt": "Don't have an account? Sign up here.",
    "welcome_message": "Welcome back, {user}! Your financial dashboard is up to date.",
    "password_reset_notice": "A password recovery link has been sent to {email}.",
    "invoice_summary": "You have {count} pending invoices awaiting approval for {company}."
}

ACCEPTANCE_CRITERIA_SPEC = [
    {
        "name": "bundle_deliverable_completeness",
        "description": "Requires both es_translations.json and landing_page_es.md to be present in deliverable bundle."
    },
    {
        "name": "placeholder_preservation",
        "description": "Preserves all curly-brace interpolation tokens verbatim ({user}, {email}, {count}, {company})."
    },
    {
        "name": "required_keys_present",
        "description": "Guarantees 100% parity with source UI dictionary; no dropped strings."
    },
    {
        "name": "landing_page_required_sections",
        "description": "Requires Markdown H1 title and 4 mandatory H2 sections: Problema, Solución, Características, Llamado a la Acción."
    },
    {
        "name": "landing_page_word_count",
        "description": "Enforces concise, bounded copy length between 120 and 500 words."
    },
    {
        "name": "landing_page_factual_claim_safety",
        "description": "Rejects unauthorized regulatory (FDIC) or guaranteed return claims."
    }
]

RATIONALE_EXPLANATION = (
    "These acceptance criteria are selected to ensure software reliability and brand safety: "
    "1) Strict placeholder preservation prevents runtime string formatting exceptions in the frontend application. "
    "2) 100% key parity ensures no untranslated English strings appear in the localized user interface. "
    "3) The 4-section landing page structure guarantees marketing conversion readability without bloating. "
    "4) Automated factual claim screening prevents deceptive or legally non-compliant financial claims before payment settlement."
)

def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Safely extracts a JSON object from text, handling markdown fences and extraneous prose."""
    if not text:
        return None
    cleaned = text.strip()
    try:
        val = json.loads(cleaned)
        if isinstance(val, dict):
            return val
    except Exception:
        pass

    m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        try:
            val = json.loads(m.group(1).strip())
            if isinstance(val, dict):
                return val
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            val = json.loads(text[start:end+1])
            if isinstance(val, dict):
                return val
        except Exception:
            pass
    return None

class BuyerAgent:
    """
    Buyer Agent: Conversational Assistant for Contract Formulation & Payment Safety.
    
    Responsibilities:
    - Parses natural-language buyer outcome requirements into structured contracts.
    - Extracts deliverables, acceptance criteria, and budget.
    - Clarifies missing or contradictory input.
    - Provides auditable explanations for verification findings and payment gating.
    - Enforces that contract amounts and verification rules remain under backend control.
    """

    @classmethod
    async def formulate_proposal(
        cls,
        user_prompt: str,
        simulate_missing_info: bool = False,
        simulate_contradiction: bool = False,
        force_fallback: bool = False
    ) -> ContractProposalResponse:
        logger.info(f"BuyerAgent formulating proposal from prompt: '{user_prompt[:60]}...'")

        # 1. Handle simulated test scenarios
        if simulate_missing_info:
            return ContractProposalResponse(
                title="Incomplete Contract Request",
                description="The request lacks essential deliverables or budget constraints.",
                budget_amount="0.00",
                currency="USD",
                requested_deliverables=[],
                acceptance_criteria=[],
                acceptance_criteria_rationale="No criteria can be formulated without deliverable specifications.",
                clarification_needed="Please specify the target deliverables, source text/strings to translate, and your approved budget.",
                is_valid=False,
                source_strings={}
            )

        if simulate_contradiction:
            return ContractProposalResponse(
                title="Contradictory Contract Terms",
                description="Contradiction detected: The request specified $0 budget while requiring commercial deliverables.",
                budget_amount="0.00",
                currency="USD",
                requested_deliverables=["es_translations.json"],
                acceptance_criteria=[],
                acceptance_criteria_rationale="Conflicting specifications cannot be converted into an active payment contract.",
                clarification_needed="Contradiction detected: Requested budget is $0.00, but multi-agent deliverable generation requires an authorized budget allocation.",
                is_valid=False,
                source_strings=DEFAULT_SOURCE_STRINGS
            )

        # 2. Extract Budget with trusted server-side bounds
        # Prioritize explicit budget statements to defend against prompt-injection overrides
        budget_match = re.search(r"(?:budget|allocation|cost|price|presupuesto)\s*[:=]?\s*\$?\s*(\d+(?:\.\d{1,2})?)", user_prompt, re.IGNORECASE)
        if not budget_match:
            budget_match = re.search(r"\$\s*(\d+(?:\.\d{1,2})?)", user_prompt)
        if not budget_match:
            budget_match = re.search(r"(\d+(?:\.\d{1,2})?)\s*(?:USD|dollars)", user_prompt, re.IGNORECASE)
            
        extracted_budget = "40.00"
        if budget_match:
            try:
                amt = float(budget_match.group(1))
                if amt <= 0:
                    return ContractProposalResponse(
                        title="Invalid Budget",
                        description="Budget must be greater than zero.",
                        budget_amount="0.00",
                        currency="USD",
                        requested_deliverables=[],
                        acceptance_criteria=[],
                        acceptance_criteria_rationale="Contracts must have a positive financial allocation for PayPal authorization.",
                        clarification_needed="The specified budget must be greater than $0.00 USD.",
                        is_valid=False,
                        source_strings={}
                    )
                extracted_budget = f"{amt:.2f}"
            except ValueError:
                extracted_budget = "40.00"

        # 3. Detect Deliverables from Prompt
        deliverables = []
        prompt_lower = user_prompt.lower()
        if "translat" in prompt_lower or "string" in prompt_lower or "ui" in prompt_lower or "spanish" in prompt_lower:
            deliverables.append("es_translations.json")
        if "landing" in prompt_lower or "copy" in prompt_lower or "page" in prompt_lower:
            deliverables.append("landing_page_es.md")
        # QA Agent report is standard for quality verification
        deliverables.append("qa_report.json")

        title = "Spanish Market Launch Kit"
        description = "Localization of UI strings with placeholder preservation and high-converting Spanish landing page copy."
        
        # 4. Optional Live LLM Enrichment if configured
        rationale_text = RATIONALE_EXPLANATION
        if not force_fallback and llm_client.is_live_configured:
            try:
                llm_prompt = (
                    f"Analyze this buyer procurement request:\n"
                    f"'{user_prompt}'\n\n"
                    f"Formulate a structured contract proposal in valid JSON format with keys:\n"
                    f"- 'title': concise professional title\n"
                    f"- 'description': detailed scope of work\n"
                    f"- 'proposed_budget': string amount or null\n"
                    f"- 'currency': currency code (e.g. 'USD')\n"
                    f"- 'requested_deliverables': list of expected output files\n"
                    f"- 'clarification_needed': string describing missing or contradictory info, or null if complete\n"
                    f"- 'acceptance_criteria_rationale': string explaining why strict verification criteria are required\n"
                    f"Respond ONLY with the JSON object."
                )
                fallback_obj = {
                    "title": title,
                    "description": description,
                    "proposed_budget": extracted_budget,
                    "currency": "USD",
                    "requested_deliverables": deliverables,
                    "clarification_needed": None,
                    "acceptance_criteria_rationale": RATIONALE_EXPLANATION
                }
                res = await llm_client.generate(
                    prompt=llm_prompt,
                    system_instruction="You are an autonomous procurement AI creating clear, concise digital work contracts with strict safety boundaries.",
                    fallback_content=json.dumps(fallback_obj)
                )
                if not res.is_fallback:
                    parsed = extract_json_object(res.content)
                    if parsed:
                        if parsed.get("clarification_needed"):
                            return ContractProposalResponse(
                                title="Clarification Required",
                                description=parsed.get("description", description),
                                budget_amount="0.00",
                                currency="USD",
                                requested_deliverables=[],
                                acceptance_criteria=[],
                                acceptance_criteria_rationale="No criteria can be finalized until requirements are clarified.",
                                clarification_needed=parsed["clarification_needed"],
                                is_valid=False,
                                source_strings={}
                            )
                        title = parsed.get("title", title)
                        description = parsed.get("description", description)
                        if parsed.get("requested_deliverables") and isinstance(parsed["requested_deliverables"], list):
                            deliverables = [str(d) for d in parsed["requested_deliverables"] if d]
                        if parsed.get("acceptance_criteria_rationale"):
                            rationale_text = f"{parsed['acceptance_criteria_rationale']} {RATIONALE_EXPLANATION}"
            except Exception as e:
                logger.warning(f"BuyerAgent live LLM enrichment failed, falling back to deterministic: {e}")

        return ContractProposalResponse(
            title=title,
            description=description,
            budget_amount=extracted_budget,
            currency="USD",
            requested_deliverables=deliverables,
            acceptance_criteria=ACCEPTANCE_CRITERIA_SPEC,
            acceptance_criteria_rationale=rationale_text,
            clarification_needed=None,
            is_valid=True,
            source_strings=DEFAULT_SOURCE_STRINGS
        )

    @classmethod
    def explain_gate_decision(
        cls,
        contract_status: str,
        findings: List[Dict[str, Any]],
        has_active_hold: bool
    ) -> Dict[str, str]:
        """
        Produces an auditable explanation of why payment release is permitted or blocked.
        """
        mandatory_failures = [f for f in findings if f.get("is_mandatory", True) and not f.get("passed", False)]
        
        if mandatory_failures:
            failed_names = ", ".join([f.get("criterion_name", "unknown") for f in mandatory_failures])
            return {
                "decision": "BLOCKED",
                "headline": "Payment Capture Strictly Blocked: Mandatory Verification Failed",
                "explanation": (
                    f"Payment capture cannot proceed because {len(mandatory_failures)} mandatory verification check(s) failed: {failed_names}. "
                    "The authoritative server-side payment gate protects buyer funds. You may re-execute the workflow or void the authorization hold at $0 charge."
                ),
                "recommended_action": "Fix deliverables via re-execution or void authorization hold."
            }
        
        if not has_active_hold:
            return {
                "decision": "PENDING_HOLD",
                "headline": "Awaiting PayPal Authorization Hold",
                "explanation": "Deliverables cannot be settled until an authorization hold has been confirmed on PayPal rails.",
                "recommended_action": "Create and confirm PayPal Sandbox authorization hold."
            }

        if contract_status == "AWAITING_BUYER_APPROVAL":
            return {
                "decision": "UNLOCKED",
                "headline": "Payment Gate Unlocked: Ready for Human Buyer Approval",
                "explanation": (
                    "All 10 mandatory deterministic verification checks have passed completely and an active PayPal authorization hold is in place. "
                    "In compliance with human-governed safety policy, funds can only be captured when you click 'Approve Deliverable & Capture'."
                ),
                "recommended_action": "Review generated artifacts and approve capture."
            }

        if contract_status == "PAID":
            return {
                "decision": "SETTLED",
                "headline": "Contract Successfully Settled",
                "explanation": "Funds were captured following full verification pass and explicit buyer authorization sign-off.",
                "recommended_action": "Download deliverable bundle and inspect immutable audit receipt."
            }

        return {
            "decision": "IN_PROGRESS",
            "headline": f"Workflow In Progress: {contract_status}",
            "explanation": f"Contract is currently in {contract_status} state. Awaiting completion of agent execution and verification.",
            "recommended_action": "Wait for agent deliverables to complete."
        }
