from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.modelos.agendamento import Agendamento
from app.modelos.paciente import Paciente
from app.modelos.profissional import Profissional
from app.modelos.especialidade import Especialidade
from app.modelos.local_atendimento import LocalAtendimento
from app.schemas.agendamento import AgendamentoCreate, AgendamentoOut, AgendamentoUpdate

router = APIRouter(prefix="/api/agendamentos", tags=["Agendamentos"])


def _validar_fk(payload: dict, db: Session):
    if "paciente_id" in payload and payload["paciente_id"] is not None:
        if not db.get(Paciente, payload["paciente_id"]):
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if "profissional_id" in payload and payload["profissional_id"] is not None:
        if not db.get(Profissional, payload["profissional_id"]):
            raise HTTPException(status_code=404, detail="Profissional não encontrado.")
    if "especialidade_id" in payload and payload["especialidade_id"] is not None:
        if not db.get(Especialidade, payload["especialidade_id"]):
            raise HTTPException(status_code=404, detail="Especialidade não encontrada.")
    if "local_id" in payload and payload["local_id"] is not None:
        if not db.get(LocalAtendimento, payload["local_id"]):
            raise HTTPException(status_code=404, detail="Local não encontrado.")


def _validar_conflito(profissional_id: int, inicio, db: Session, ignore_id: int | None = None):
    stmt = select(Agendamento).where(
        and_(
            Agendamento.profissional_id == profissional_id,
            Agendamento.inicio == inicio,
        )
    )
    if ignore_id is not None:
        stmt = stmt.where(Agendamento.id != ignore_id)

    exists = db.scalar(stmt)
    if exists:
        raise HTTPException(status_code=409, detail="Conflito: já existe agendamento neste horário para o profissional.")


def _validar_telemedicina(especialidade_id: int, modalidade: str, db: Session):
    if modalidade != "TELEMEDICINA":
        return

    esp = db.get(Especialidade, especialidade_id)
    if not esp:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")

    if not esp.permite_telemedicina:
        raise HTTPException(status_code=400, detail="Esta especialidade não permite telemedicina.")


@router.post("", response_model=AgendamentoOut, status_code=status.HTTP_201_CREATED)
def criar(payload: AgendamentoCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["status"] = "agendado"

    _validar_fk(data, db)
    _validar_telemedicina(data["especialidade_id"], data["modalidade"], db)
    _validar_conflito(data["profissional_id"], data["inicio"], db)

    obj = Agendamento(**data)
    db.add(obj)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito: agendamento já existe para este horário/profissional.")

    db.refresh(obj)
    return obj


@router.get("", response_model=list[AgendamentoOut])
def listar(db: Session = Depends(get_db)):
    return list(db.scalars(select(Agendamento).order_by(Agendamento.inicio.desc())).all())


@router.get("/{agendamento_id}", response_model=AgendamentoOut)
def detalhar(agendamento_id: int, db: Session = Depends(get_db)):
    obj = db.get(Agendamento, agendamento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    return obj


@router.put("/{agendamento_id}", response_model=AgendamentoOut)
def atualizar(agendamento_id: int, payload: AgendamentoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Agendamento, agendamento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data:
        data["status"] = "agendado"

    _validar_fk(data, db)

    profissional_id = data.get("profissional_id", obj.profissional_id)
    inicio = data.get("inicio", obj.inicio)
    especialidade_id = data.get("especialidade_id", obj.especialidade_id)
    modalidade = data.get("modalidade", obj.modalidade)

    _validar_telemedicina(especialidade_id, modalidade, db)
    _validar_conflito(profissional_id, inicio, db, ignore_id=obj.id)

    for k, v in data.items():
        setattr(obj, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito: agendamento já existe para este horário/profissional.")

    db.refresh(obj)
    return obj


@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(agendamento_id: int, db: Session = Depends(get_db)):
    obj = db.get(Agendamento, agendamento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    db.delete(obj)
    db.commit()
    return None
