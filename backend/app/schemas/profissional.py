from pydantic import BaseModel, Field


class ProfissionalBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    especialidade_id: int


class ProfissionalCreate(ProfissionalBase):
    pass


class ProfissionalUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    especialidade_id: int | None = None


class ProfissionalOut(BaseModel):
    id: int
    nome: str
    especialidade_id: int

    class Config:
        from_attributes = True
