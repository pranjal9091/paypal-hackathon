import json
import re
from typing import Dict, List, Tuple, Optional

class VerificationFindingResult:
    def __init__(
        self,
        criterion_name: str,
        passed: bool,
        details: str,
        deliverable_filename: Optional[str] = None,
        evaluator: str = "deterministic",
        is_mandatory: bool = True
    ):
        self.criterion_name = criterion_name
        self.passed = passed
        self.details = details
        self.deliverable_filename = deliverable_filename
        self.evaluator = evaluator
        self.is_mandatory = is_mandatory

class DeterministicVerifier:
    """
    Independent Multi-Artifact Verification Engine for Outcome Exchange.
    Validates complete deliverable bundles across both deterministic criteria and QA reviews.
    Mandatory Rules:
    - All required bundle deliverables must exist.
    - JSON deliverables must satisfy syntax, key parity, placeholders, and value integrity.
    - Markdown deliverables must satisfy structural hierarchy, section completeness, word-count, and claim safety.
    - Deterministic checks are strictly mandatory (fails closed).
    - QA Agent findings provide qualitative context without altering mandatory pass/fail gates.
    """

    PLACEHOLDER_REGEX = re.compile(r"\{([a-zA-Z0-9_]+)\}")
    FORBIDDEN_CLAIMS = [
        "banco autorizado",
        "licencia bancaria oficial",
        "100% rentabilidad",
        "garantía de 100%",
        "garantizado por ley"
    ]

    REQUIRED_LANDING_SECTIONS = [
        "## El Problema",
        "## La Solución",
        "## Características",
        "## Llamado a la Acción"
    ]

    @classmethod
    def verify_bundle(
        cls,
        source_strings: Dict[str, str],
        deliverables_by_filename: Dict[str, str]
    ) -> Tuple[bool, List[VerificationFindingResult]]:
        findings: List[VerificationFindingResult] = []

        # Check 1: Bundle Completeness
        has_translations = "es_translations.json" in deliverables_by_filename
        has_landing = "landing_page_es.md" in deliverables_by_filename

        if not has_translations or not has_landing:
            missing = []
            if not has_translations: missing.append("es_translations.json")
            if not has_landing: missing.append("landing_page_es.md")
            findings.append(VerificationFindingResult(
                criterion_name="bundle_deliverable_completeness",
                passed=False,
                details=f"Mandatory deliverable bundle incomplete. Missing: {missing}",
                is_mandatory=True
            ))
            return False, findings
        else:
            findings.append(VerificationFindingResult(
                criterion_name="bundle_deliverable_completeness",
                passed=True,
                details="All mandatory bundle artifacts (es_translations.json, landing_page_es.md) are present.",
                is_mandatory=True
            ))

        # Check 2: Verify es_translations.json
        translations_raw = deliverables_by_filename["es_translations.json"]
        loc_passed, loc_findings = cls.verify_translations(source_strings, translations_raw)
        findings.extend(loc_findings)

        # Check 3: Verify landing_page_es.md
        landing_raw = deliverables_by_filename["landing_page_es.md"]
        landing_passed, landing_findings = cls.verify_landing_page(landing_raw)
        findings.extend(landing_findings)

        # Check 4: Include QA Agent Report Findings if available
        if "qa_report.json" in deliverables_by_filename:
            qa_findings = cls.extract_qa_findings(deliverables_by_filename["qa_report.json"])
            findings.extend(qa_findings)

        # Fail closed: ALL mandatory checks must pass
        mandatory_passed = all(f.passed for f in findings if f.is_mandatory)
        return mandatory_passed, findings

    @classmethod
    def verify_translations(
        cls,
        source_strings: Dict[str, str],
        deliverable_content: str
    ) -> Tuple[bool, List[VerificationFindingResult]]:
        findings: List[VerificationFindingResult] = []
        filename = "es_translations.json"

        # 2a. JSON Syntax
        parsed_json = None
        try:
            parsed_json = json.loads(deliverable_content)
            if not isinstance(parsed_json, dict):
                findings.append(VerificationFindingResult(
                    criterion_name="json_syntax_validity",
                    passed=False,
                    details="Deliverable content parsed as JSON but root element is not a JSON object.",
                    deliverable_filename=filename
                ))
                return False, findings
            findings.append(VerificationFindingResult(
                criterion_name="json_syntax_validity",
                passed=True,
                details="Valid JSON object structure confirmed.",
                deliverable_filename=filename
            ))
        except Exception as e:
            findings.append(VerificationFindingResult(
                criterion_name="json_syntax_validity",
                passed=False,
                details=f"JSON parsing failed with error: {str(e)}",
                deliverable_filename=filename
            ))
            return False, findings

        # 2b. Key Parity (Every source key must exist in translation)
        missing_keys = [k for k in source_strings.keys() if k not in parsed_json]
        if missing_keys:
            findings.append(VerificationFindingResult(
                criterion_name="required_keys_present",
                passed=False,
                details=f"Missing {len(missing_keys)} required source keys: {missing_keys}",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="required_keys_present",
                passed=True,
                details=f"All {len(source_strings)} required source keys are present.",
                deliverable_filename=filename
            ))

        # 2c. Unexpected Keys Check
        unexpected_keys = [k for k in parsed_json.keys() if k not in source_strings]
        if unexpected_keys:
            findings.append(VerificationFindingResult(
                criterion_name="unexpected_keys_policy",
                passed=False,
                details=f"Found {len(unexpected_keys)} unexpected unauthorized keys in deliverable: {unexpected_keys}",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="unexpected_keys_policy",
                passed=True,
                details="No unauthorized extra keys detected.",
                deliverable_filename=filename
            ))

        # 2d. Non-empty string values
        empty_keys = []
        non_string_keys = []
        for k, v in parsed_json.items():
            if not isinstance(v, str):
                non_string_keys.append(k)
            elif not v.strip():
                empty_keys.append(k)

        if empty_keys or non_string_keys:
            err_msg = []
            if empty_keys: err_msg.append(f"Empty values for keys: {empty_keys}")
            if non_string_keys: err_msg.append(f"Non-string types for keys: {non_string_keys}")
            findings.append(VerificationFindingResult(
                criterion_name="non_empty_translations",
                passed=False,
                details="; ".join(err_msg),
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="non_empty_translations",
                passed=True,
                details="All translation values are valid non-empty strings.",
                deliverable_filename=filename
            ))

        # 2e. Placeholder Preservation
        placeholder_failures = []
        for key, src_val in source_strings.items():
            if key in parsed_json and isinstance(parsed_json[key], str):
                src_placeholders = set(cls.PLACEHOLDER_REGEX.findall(src_val))
                tgt_placeholders = set(cls.PLACEHOLDER_REGEX.findall(parsed_json[key]))

                missing_in_target = src_placeholders - tgt_placeholders
                if missing_in_target:
                    placeholder_failures.append(
                        f"Key '{key}' missing required placeholders: {list(missing_in_target)}"
                    )

        if placeholder_failures:
            findings.append(VerificationFindingResult(
                criterion_name="placeholder_preservation",
                passed=False,
                details="; ".join(placeholder_failures),
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="placeholder_preservation",
                passed=True,
                details="All variable placeholders ({variable}) preserved verbatim across all strings.",
                deliverable_filename=filename
            ))

        loc_passed = all(f.passed for f in findings)
        return loc_passed, findings

    @classmethod
    def verify_landing_page(
        cls,
        markdown_content: str
    ) -> Tuple[bool, List[VerificationFindingResult]]:
        findings: List[VerificationFindingResult] = []
        filename = "landing_page_es.md"
        content_stripped = markdown_content.strip()

        # 3a. H1 Document Title Check
        if not re.search(r"^#\s+[^\n]+", content_stripped, flags=re.MULTILINE):
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_h1_title",
                passed=False,
                details="Document missing required top-level H1 title ('# Product Title').",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_h1_title",
                passed=True,
                details="Top-level H1 document title present.",
                deliverable_filename=filename
            ))

        # 3b. Required H2 Sections Check
        missing_sections = []
        for sec in cls.REQUIRED_LANDING_SECTIONS:
            # Check flexible match for Spanish section titles
            keyword = sec.replace("##", "").strip().lower()
            if keyword not in content_stripped.lower():
                missing_sections.append(sec)

        if missing_sections:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_required_sections",
                passed=False,
                details=f"Missing {len(missing_sections)} required sections: {missing_sections}",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_required_sections",
                passed=True,
                details="All 4 required sections (Problema, Solución, Características, Llamado a la Acción) present.",
                deliverable_filename=filename
            ))

        # 3c. Word Count Check (120 - 500 words)
        words = content_stripped.split()
        word_count = len(words)
        if word_count < 120 or word_count > 500:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_word_count",
                passed=False,
                details=f"Word count {word_count} is outside the allowed range (120 - 500 words).",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_word_count",
                passed=True,
                details=f"Word count ({word_count} words) satisfies length rubric (120 - 500 words).",
                deliverable_filename=filename
            ))

        # 3d. Unsupported Claims Check
        found_forbidden = []
        for claim in cls.FORBIDDEN_CLAIMS:
            if claim in content_stripped.lower():
                found_forbidden.append(claim)

        if found_forbidden:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_factual_claim_safety",
                passed=False,
                details=f"Deliverable contains unsupported/exaggerated claims: {found_forbidden}",
                deliverable_filename=filename
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="landing_page_factual_claim_safety",
                passed=True,
                details="No prohibited or unsupported regulatory/financial claims detected.",
                deliverable_filename=filename
            ))

        landing_passed = all(f.passed for f in findings)
        return landing_passed, findings

    @classmethod
    def extract_qa_findings(cls, qa_content: str) -> List[VerificationFindingResult]:
        """
        Extracts QA Agent review findings as informative, non-mandatory checks.
        """
        findings = []
        try:
            report = json.loads(qa_content)
            verdict = report.get("verdict", "PASS")
            score = report.get("score", 100)
            summary = report.get("review_summary", "")

            findings.append(VerificationFindingResult(
                criterion_name="qa_agent_overall_review",
                passed=(verdict == "PASS"),
                details=f"QA Verdict: {verdict} (Score: {score}/100). {summary}",
                deliverable_filename="qa_report.json",
                evaluator="qa_agent",
                is_mandatory=False # QA opinions do not override deterministic security gate
            ))
        except Exception:
            findings.append(VerificationFindingResult(
                criterion_name="qa_agent_overall_review",
                passed=False,
                details="Failed to parse structured QA report JSON.",
                deliverable_filename="qa_report.json",
                evaluator="qa_agent",
                is_mandatory=False
            ))
        return findings

    # Backwards-compatibility helper for Milestone 1 single-deliverable calls
    @classmethod
    def verify(cls, source_strings: Dict[str, str], deliverable_content: str) -> Tuple[bool, List[VerificationFindingResult]]:
        return cls.verify_translations(source_strings, deliverable_content)
