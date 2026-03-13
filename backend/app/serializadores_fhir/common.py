from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


CPF_NAMING_SYSTEM = "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cpf"
CNS_NAMING_SYSTEM = "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cns"
CRM_NAMING_SYSTEM = "http://rnds.saude.gov.br/fhir/r4/NamingSystem/crm"
MOTHERS_MAIDEN_NAME_URL = (
    "http://hl7.org/fhir/StructureDefinition/patient-mothersMaidenName"
)
DEFAULT_BUNDLE_TIMEZONE = ZoneInfo("America/Fortaleza")


def only_digits(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\D+", "", str(value))


def normalize_cpf(value: Any) -> str | None:
    digits = only_digits(value)
    return digits or None


def normalize_cns(value: Any) -> str | None:
    digits = only_digits(value)
    return digits or None


def normalize_crm(value: Any, uf: Any = None) -> str | None:
    digits = only_digits(value)
    if not digits:
        return None

    uf_value = re.sub(r"[^A-Za-z]+", "", str(uf or "")).upper()
    if uf_value:
        return f"{uf_value}{digits}"
    return digits


def normalize_gender(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if not normalized:
        return None

    gender_map = {
        "m": "male",
        "masculino": "male",
        "male": "male",
        "f": "female",
        "feminino": "female",
        "female": "female",
        "outro": "other",
        "other": "other",
        "nao informado": "unknown",
        "não informado": "unknown",
        "desconhecido": "unknown",
        "unknown": "unknown",
    }
    return gender_map.get(normalized)


def to_fhir_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None

    if value.tzinfo is None or value.utcoffset() is None:
        value = value.replace(tzinfo=DEFAULT_BUNDLE_TIMEZONE)

    return value.isoformat()
