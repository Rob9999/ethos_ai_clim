import pytest

import torch
from ethos_ai.security.exception.security_access_exception import (
    SecurityAccessException,
)
from ethos_ai.security.securied_identity_card import SecuredIdentityCard
from ethos_ai.security.security_level import SecurityLevel


@pytest.fixture
def security_level():
    return SecuredIdentityCard("Test", "password", SecurityLevel.MEDIUM)


def test_check_security_valid_password(security_level):
    required_level = SecurityLevel.LOW
    input_password = "password"
    assert security_level.check_security(required_level, input_password) is None


def test_check_security_invalid_password(security_level):
    required_level = SecurityLevel.LOW
    input_password = "wrong_password"
    with pytest.raises(SecurityAccessException):
        security_level.check_security(required_level, input_password)


def test_check_security_insufficient_level(security_level):
    required_level = SecurityLevel.HIGH
    input_password = "password"
    with pytest.raises(SecurityAccessException):
        security_level.check_security(required_level, input_password)


def test_simple_check_security():
    ethos_ai_individual_security = SecuredIdentityCard(
        name="EthosAIIndividual R.A.M.",
        password="secure123",
        security_level=SecurityLevel.MEDIUM,
        responsible="Supervisor M.M.",
    )
    # Versuch, eine Aktion mit einer höheren Sicherheitsstufe auszuführen
    try:
        ethos_ai_individual_security.check_security(SecurityLevel.HIGH, "secure123")
    except SecurityAccessException as e:
        print(f"Aktion abgebrochen: {e}")

    # Versuch, eine Aktion mit einer niedrigeren Sicherheitsstufe auszuführen
    if ethos_ai_individual_security.try_check_security(SecurityLevel.LOW, "secure123"):
        print("Aktion erfolgreich durchgeführt.")
    else:
        print("Aktion fehlgeschlagen.")
