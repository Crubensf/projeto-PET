from datetime import datetime
from pydantic import BaseModel, Field


class AgendamentoBase(BaseModel):
    paciente_id: int = Field(gt=0)
    profissional_id: int = Field(gt=0)
    especialidade_id: int = Field(gt=0)
    local_id: int = Field(gt=0)

    inicio: datetime
    modalidade: str = Field(default="PRESENCIAL",
                            pattern="^(PRESENCIAL|TELEMEDICINA)$")


    status: str = Field(
    default="agendado",
    pattern="^(agendado|cancelado|atendido)$"
    )


class AgendamentoCreate(AgendamentoBase):
    pass


class AgendamentoUpdate(BaseModel):
    paciente_id: int | None = Field(default=None, gt=0)
    profissional_id: int | None = Field(default=None, gt=0)
    especialidade_id: int | None = Field(default=None, gt=0)
    local_id: int | None = Field(default=None, gt=0)
    inicio: datetime | None = None
    modalidade: str | None = Field(
        default=None, pattern="^(PRESENCIAL|TELEMEDICINA)$")
    status: str | None = None


class AgendamentoOut(BaseModel):
    id: int
    inicio: datetime
    status: str

    paciente_id: int
    profissional_id: int
    especialidade_id: int
    local_id: int

    # 🔥 CAMPOS ADICIONADOS
    paciente_nome: str | None = None
    profissional_nome: str | None = None
    especialidade_nome: str | None = None

    class Config:
        from_attributes = True
