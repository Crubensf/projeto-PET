import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.modelos.paciente import Paciente
from app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate


router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(get_current_user)],
)


def only_digits(s: str) -> str:
    return re.sub(r"\D+", "", str(s or ""))


def is_valid_cns(cns: str) -> bool:
    return bool(re.fullmatch(r"\d{15}", cns or ""))


def is_valid_tel(tel: str) -> bool:
    return bool(re.fullmatch(r"\d{10,11}", tel or ""))


@router.get("/by-cns/{cns}", response_model=PacienteOut)
def buscar_por_cns(cns: str, db: Session = Depends(get_db)):
    cns_digits = only_digits(cns)
    if len(cns_digits) != 15:
        raise HTTPException(
            status_code=422,
            detail="CNS deve ter exatamente 15 dígitos.",
        )

    obj = db.scalar(select(Paciente).where(Paciente.cartao_sus == cns_digits))
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return obj


@router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def criar(payload: PacienteCreate, db: Session = Depends(get_db)):
   
    exists = db.scalar(
        select(Paciente).where(Paciente.cartao_sus == payload.cartao_sus)
    )
    if exists:
        raise HTTPException(
            status_code=409,
            detail="Já existe paciente com este cartão SUS.",
        )

    obj = Paciente(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=list[PacienteOut])
def listar(db: Session = Depends(get_db)):
    rows = list(db.scalars(select(Paciente).order_by(Paciente.nome)).all())

   
    invalid = [
        p for p in rows
        if not is_valid_cns(p.cartao_sus) or not is_valid_tel(p.telefone)
    ]
    if invalid:
        ids = [p.id for p in invalid][:20]
        raise HTTPException(
            status_code=500,
            detail=(
                f"Base contém pacientes inválidos (ids={ids}). "
                "Corrija CNS (15 dígitos) e telefone (10-11)."
            ),
        )

    return rows


@router.get("/{paciente_id}", response_model=PacienteOut)
def detalhar(paciente_id: int, db: Session = Depends(get_db)):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return obj


@router.put("/{paciente_id}", response_model=PacienteOut)
def atualizar(
    paciente_id: int,
    payload: PacienteUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")


    data = payload.model_dump(exclude_none=True)

    
    if "cartao_sus" in data and data["cartao_sus"] != obj.cartao_sus:
        exists = db.scalar(
            select(Paciente).where(Paciente.cartao_sus == data["cartao_sus"])
        )
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Já existe paciente com este cartão SUS.",
            )

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
