from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict

from app.core.validators import (
    sanitize_cns,
    sanitize_cpf,
    sanitize_phone,
    validate_not_future_date,
)


class PacienteBase(BaseModel):
    nome: str = Field(min_length=2, max_length=140)

    cpf: str = Field(min_length=11, max_length=11)

    cartao_sus: str = Field(min_length=15, max_length=15)

    telefone: str = Field(min_length=10, max_length=11)

    data_nascimento: date
    municipio: str = Field(min_length=2, max_length=120)
    endereco: str = Field(min_length=2, max_length=200)
    nome_mae: str = Field(min_length=2, max_length=140)

    # ---------- CPF ----------
    @field_validator("cpf", mode="before")
    @classmethod
    def validar_cpf(cls, v: Any) -> str:
        return sanitize_cpf(v)

    # ---------- CNS ----------
    @field_validator("cartao_sus", mode="before")
    @classmethod
    def validar_cns(cls, v: Any) -> str:
        if v in (None, ""):
            raise ValueError("cartao_sus é obrigatório e deve conter 15 dígitos.")
        return sanitize_cns(v)

    # ---------- TELEFONE ----------
    @field_validator("telefone", mode="before")
    @classmethod
    def validar_telefone(cls, v: Any) -> str:
        return sanitize_phone(v)

    # ---------- DATA ----------
    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, v: date) -> date:
        return validate_not_future_date(v, field_name="data_nascimento")


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=140)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=11)
    cartao_sus: Optional[str] = Field(default=None, min_length=15, max_length=15)
    telefone: Optional[str] = Field(default=None, min_length=10, max_length=11)
    data_nascimento: Optional[date] = None
    municipio: Optional[str] = Field(default=None, min_length=2, max_length=120)
    endereco: Optional[str] = Field(default=None, min_length=2, max_length=200)
    nome_mae: Optional[str] = Field(default=None, min_length=2, max_length=140)

    @field_validator("cpf", mode="before")
    @classmethod
    def validar_cpf_update(cls, v: Any) -> Any:
        if v is None:
            return v
        return sanitize_cpf(v)

    @field_validator("cartao_sus", mode="before")
    @classmethod
    def validar_cns_update(cls, v: Any) -> Any:
        if v in (None, ""):
            return None
        return sanitize_cns(v)

    @field_validator("telefone", mode="before")
    @classmethod
    def validar_telefone_update(cls, v: Any) -> Any:
        if v is None:
            return v
        return sanitize_phone(v)

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento_update(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        return validate_not_future_date(v, field_name="data_nascimento")


class PacienteOut(PacienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
