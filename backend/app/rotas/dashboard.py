from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.database import get_db
from app.modelos.paciente import Paciente
from app.modelos.profissional import Profissional
from app.modelos.especialidade import Especialidade
from app.modelos.local_atendimento import LocalAtendimento
from app.modelos.agendamento import Agendamento

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def resumo(db: Session = Depends(get_db)):
    return {
        "pacientes": db.scalar(select(func.count()).select_from(Paciente)),
        "profissionais": db.scalar(select(func.count()).select_from(Profissional)),
        "especialidades": db.scalar(select(func.count()).select_from(Especialidade)),
        "locais": db.scalar(select(func.count()).select_from(LocalAtendimento)),
        "agendamentos": db.scalar(select(func.count()).select_from(Agendamento)),
    }
