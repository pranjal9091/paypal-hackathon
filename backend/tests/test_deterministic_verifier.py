import json
import pytest
from app.verifier.deterministic_verifier import DeterministicVerifier

SOURCE_STRINGS = {
    "login_button": "Log in",
    "welcome_user": "Welcome back, {user}!",
    "reset_pass": "Reset link sent to {email}."
}

def test_verifier_passes_on_valid_deliverable():
    valid_deliverable = json.dumps({
        "login_button": "Iniciar sesión",
        "welcome_user": "¡Bienvenido de nuevo, {user}!",
        "reset_pass": "Enlace de restablecimiento enviado a {email}."
    })
    passed, findings = DeterministicVerifier.verify(SOURCE_STRINGS, valid_deliverable)
    assert passed is True
    assert all(f.passed for f in findings)
    assert len(findings) == 5

def test_verifier_fails_on_missing_key():
    missing_key_deliverable = json.dumps({
        "login_button": "Iniciar sesión",
        # "welcome_user" is missing!
        "reset_pass": "Enlace enviado a {email}."
    })
    passed, findings = DeterministicVerifier.verify(SOURCE_STRINGS, missing_key_deliverable)
    assert passed is False
    key_finding = next(f for f in findings if f.criterion_name == "required_keys_present")
    assert key_finding.passed is False
    assert "welcome_user" in key_finding.details

def test_verifier_fails_on_corrupted_placeholder():
    corrupted_placeholder_deliverable = json.dumps({
        "login_button": "Iniciar sesión",
        "welcome_user": "¡Bienvenido de nuevo, {user}!",
        "reset_pass": "Enlace enviado a tu correo electronico." # {email} missing!
    })
    passed, findings = DeterministicVerifier.verify(SOURCE_STRINGS, corrupted_placeholder_deliverable)
    assert passed is False
    placeholder_finding = next(f for f in findings if f.criterion_name == "placeholder_preservation")
    assert placeholder_finding.passed is False
    assert "reset_pass" in placeholder_finding.details

def test_verifier_fails_on_empty_translation():
    empty_translation_deliverable = json.dumps({
        "login_button": "  ", # Empty!
        "welcome_user": "¡Bienvenido, {user}!",
        "reset_pass": "Enlace a {email}."
    })
    passed, findings = DeterministicVerifier.verify(SOURCE_STRINGS, empty_translation_deliverable)
    assert passed is False
    empty_finding = next(f for f in findings if f.criterion_name == "non_empty_translations")
    assert empty_finding.passed is False

def test_verifier_fails_on_invalid_json_syntax():
    invalid_syntax = "{'login_button': 'Iniciar sesión'}" # invalid json syntax (single quotes)
    passed, findings = DeterministicVerifier.verify(SOURCE_STRINGS, invalid_syntax)
    assert passed is False
    syntax_finding = next(f for f in findings if f.criterion_name == "json_syntax_validity")
    assert syntax_finding.passed is False
