from datetime import date
from pydantic import BaseModel, Field


class PacienteBase(BaseModel):
    nome: str = Field(min_length=2, max_length=140)
    cartao_sus: str = Field(min_length=8, max_length=30)

    data_nascimento: date
    telefone: str = Field(min_length=8, max_length=30)

    municipio: str = Field(min_length=2, max_length=120)
    endereco: str = Field(min_length=2, max_length=200)

    nome_mae: str = Field(min_length=2, max_length=140)


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=140)
    cartao_sus: str | None = Field(default=None, min_length=8, max_length=30)
    data_nascimento: date | None = None
    telefone: str | None = Field(default=None, min_length=8, max_length=30)
    municipio: str | None = Field(default=None, min_length=2, max_length=120)
    endereco: str | None = Field(default=None, min_length=2, max_length=200)
    nome_mae: str | None = Field(default=None, min_length=2, max_length=140)


class PacienteOut(PacienteBase):
    id: int

    class Config:
        from_attributes = True
