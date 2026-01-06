from datetime import datetime
from pydantic import BaseModel, Field


class AgendamentoBase(BaseModel):
    paciente_id: int
    profissional_id: int
    especialidade_id: int
    local_id: int

    inicio: datetime
    modalidade: str = Field(default="PRESENCIAL", pattern="^(PRESENCIAL|TELEMEDICINA)$")
    status: str = Field(default="booked")


class AgendamentoCreate(AgendamentoBase):
    pass


class AgendamentoUpdate(BaseModel):
    paciente_id: int | None = None
    profissional_id: int | None = None
    especialidade_id: int | None = None
    local_id: int | None = None
    inicio: datetime | None = None
    modalidade: str | None = Field(default=None, pattern="^(PRESENCIAL|TELEMEDICINA)$")
    status: str | None = None


class AgendamentoOut(AgendamentoBase):
    id: int

    class Config:
        from_attributes = True
