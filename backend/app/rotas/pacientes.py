from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.modelos.paciente import Paciente
from app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate

router = APIRouter(prefix="/api/pacientes", tags=["Pacientes"])


@router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def criar(payload: PacienteCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Paciente).where(Paciente.cartao_sus == payload.cartao_sus))
    if exists:
        raise HTTPException(status_code=409, detail="Já existe paciente com este cartão SUS.")
    obj = Paciente(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=list[PacienteOut])
def listar(db: Session = Depends(get_db)):
    return list(db.scalars(select(Paciente).order_by(Paciente.nome)).all())


@router.get("/{paciente_id}", response_model=PacienteOut)
def detalhar(paciente_id: int, db: Session = Depends(get_db)):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return obj


@router.put("/{paciente_id}", response_model=PacienteOut)
def atualizar(paciente_id: int, payload: PacienteUpdate, db: Session = Depends(get_db)):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    data = payload.model_dump(exclude_unset=True)
    if "cartao_sus" in data and data["cartao_sus"] != obj.cartao_sus:
        exists = db.scalar(select(Paciente).where(Paciente.cartao_sus == data["cartao_sus"]))
        if exists:
            raise HTTPException(status_code=409, detail="Já existe paciente com este cartão SUS.")

    for k, v in data.items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(paciente_id: int, db: Session = Depends(get_db)):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    db.delete(obj)
    db.commit()
    return None
