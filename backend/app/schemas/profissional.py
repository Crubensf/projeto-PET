from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.core.validators import only_digits, sanitize_phone


class ProfissionalBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    especialidade_id: int = Field(gt=0)

    crm: str | None = Field(default=None, max_length=20)
    crm_uf: str | None = Field(default=None, min_length=2, max_length=2)

    telefone: str | None = Field(default=None, min_length=10, max_length=11)
    email: EmailStr | None = None

    ativo: bool = True

    @field_validator("crm", mode="before")
    @classmethod
    def validar_crm(cls, v: Any) -> Any:
        if v is None:
            return v
        # CRM só números
        return only_digits(v)

    @field_validator("crm_uf")
    @classmethod
    def validar_uf(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("crm_uf deve conter exatamente 2 caracteres.")
        return v.upper()

    @field_validator("telefone", mode="before")
    @classmethod
    def validar_telefone(cls, v: Any) -> Any:
        if v is None:
            return v
        return sanitize_phone(v)


class ProfissionalCreate(ProfissionalBase):
    pass


class ProfissionalUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    especialidade_id: int | None = Field(default=None, gt=0)

    crm: str | None = Field(default=None, max_length=20)
    crm_uf: str | None = Field(default=None, min_length=2, max_length=2)

    telefone: str | None = Field(default=None, min_length=10, max_length=11)
    email: EmailStr | None = None
    ativo: bool | None = None

    @field_validator("crm", mode="before")
    @classmethod
    def validar_crm_up(cls, v: Any) -> Any:
        if v is None:
            return v
        return only_digits(v)

    @field_validator("crm_uf")
    @classmethod
    def validar_uf_up(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("crm_uf deve conter exatamente 2 caracteres.")
        return v.upper()

    @field_validator("telefone", mode="before")
    @classmethod
    def validar_telefone_up(cls, v: Any) -> Any:
        if v is None:
            return v
        return sanitize_phone(v)


class ProfissionalOut(BaseModel):
    id: int
    nome: str
    especialidade_id: int

    crm: str | None = None
    crm_uf: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    ativo: bool

    class Config:
        from_attributes = True
