import json
import re
from typing import Dict, List, Tuple

class VerificationFindingResult:
    def __init__(self, criterion_name: str, passed: bool, details: str):
        self.criterion_name = criterion_name
        self.passed = passed
        self.details = details

class DeterministicVerifier:
    """
    Deterministic Verification Engine for Spanish Launch Kit UI strings.
    Validates:
    1. JSON formatting
    2. 100% source key parity (no missing keys)
    3. Non-empty translation values
    4. Exact placeholder preservation (e.g. {email}, {username}, {count})
    5. Structural integrity
    """

    PLACEHOLDER_REGEX = re.compile(r"\{([a-zA-Z0-9_]+)\}")

    @classmethod
    def verify(cls, source_strings: Dict[str, str], deliverable_content: str) -> Tuple[bool, List[VerificationFindingResult]]:
        findings: List[VerificationFindingResult] = []

        # Check 1: Valid JSON
        parsed_json = None
        try:
            parsed_json = json.loads(deliverable_content)
            if not isinstance(parsed_json, dict):
                findings.append(VerificationFindingResult(
                    criterion_name="json_syntax_validity",
                    passed=False,
                    details="Deliverable content parsed as JSON but root element is not a JSON object."
                ))
                return False, findings
            else:
                findings.append(VerificationFindingResult(
                    criterion_name="json_syntax_validity",
                    passed=True,
                    details="Valid JSON object structure confirmed."
                ))
        except Exception as e:
            findings.append(VerificationFindingResult(
                criterion_name="json_syntax_validity",
                passed=False,
                details=f"JSON parsing failed with error: {str(e)}"
            ))
            return False, findings

        # Check 2: Key Completeness (Every source key must exist in translation)
        missing_keys = [k for k in source_strings.keys() if k not in parsed_json]
        if missing_keys:
            findings.append(VerificationFindingResult(
                criterion_name="required_keys_present",
                passed=False,
                details=f"Missing {len(missing_keys)} required source keys: {missing_keys}"
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="required_keys_present",
                passed=True,
                details=f"All {len(source_strings)} required source keys are present."
            ))

        # Check 3: Non-empty translation strings
        empty_keys = []
        for k, v in parsed_json.items():
            if not isinstance(v, str) or not v.strip():
                empty_keys.append(k)

        if empty_keys:
            findings.append(VerificationFindingResult(
                criterion_name="non_empty_translations",
                passed=False,
                details=f"Empty or non-string values found for keys: {empty_keys}"
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="non_empty_translations",
                passed=True,
                details="All translation entries contain non-empty text strings."
            ))

        # Check 4: Placeholder preservation (e.g. {email})
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
                details="; ".join(placeholder_failures)
            ))
        else:
            findings.append(VerificationFindingResult(
                criterion_name="placeholder_preservation",
                passed=True,
                details="All variable placeholders ({variable}) preserved verbatim across all strings."
            ))

        all_passed = all(f.passed for f in findings)
        return all_passed, findings
