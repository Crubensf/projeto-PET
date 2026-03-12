from __future__ import annotations

import re
from datetime import date
from typing import Any


def only_digits(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\D+", "", str(value))


def normalize_phone_digits(digits: str) -> str:
    # Remove DDI +55 quando o número vier completo.
    if len(digits) in (12, 13) and digits.startswith("55"):
        return digits[2:]
    return digits


def sanitize_cpf(value: Any) -> str:
    digits = only_digits(value)
    if len(digits) != 11:
        raise ValueError("CPF deve conter exatamente 11 dígitos.")
    return digits


def sanitize_cns(value: Any) -> str:
    digits = only_digits(value)
    if len(digits) != 15:
        raise ValueError("CNS deve conter exatamente 15 dígitos.")
    return digits


def sanitize_phone(value: Any) -> str:
    digits = normalize_phone_digits(only_digits(value))
    if len(digits) not in (10, 11):
        raise ValueError("Telefone deve conter 10 ou 11 dígitos (DDD + número).")
    return digits


def sanitize_cep(value: Any) -> str:
    digits = only_digits(value)
    if len(digits) != 8:
        raise ValueError("CEP deve conter exatamente 8 dígitos.")
    return digits


def validate_not_future_date(value: date, *, field_name: str) -> date:
    if value > date.today():
        raise ValueError(f"{field_name} não pode ser no futuro.")
    return value


def is_valid_cpf(value: Any) -> bool:
    return len(only_digits(value)) == 11


def is_valid_cns(value: Any) -> bool:
    return len(only_digits(value)) == 15


def is_valid_phone(value: Any) -> bool:
    digits = normalize_phone_digits(only_digits(value))
    return len(digits) in (10, 11)


def is_valid_cep(value: Any) -> bool:
    return len(only_digits(value)) == 8
