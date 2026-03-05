from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.modelos.especialidade import Especialidade
from app.schemas.especialidade import EspecialidadeCreate, EspecialidadeOut, EspecialidadeUpdate

router = APIRouter(prefix="/api/especialidades", tags=["Especialidades"])


@router.post("", response_model=EspecialidadeOut, status_code=status.HTTP_201_CREATED)
def criar(payload: EspecialidadeCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Especialidade).where(Especialidade.codigo == payload.codigo))
    if exists:
        raise HTTPException(status_code=409, detail="Já existe especialidade com este código.")
    obj = Especialidade(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito de unicidade para código da especialidade.")
    db.refresh(obj)
    return obj


@router.get("", response_model=list[EspecialidadeOut])
def listar(db: Session = Depends(get_db)):
    return list(db.scalars(select(Especialidade).order_by(Especialidade.nome)).all())


@router.get("/{especialidade_id}", response_model=EspecialidadeOut)
def detalhar(especialidade_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, especialidade_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")
    return obj


@router.put("/{especialidade_id}", response_model=EspecialidadeOut)
def atualizar(especialidade_id: int, payload: EspecialidadeUpdate, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, especialidade_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")

    data = payload.model_dump(exclude_unset=True)
    for campo in ("codigo", "nome", "permite_telemedicina"):
        if campo in data and data[campo] is None:
            raise HTTPException(
                status_code=422,
                detail=f"Campo obrigatório não pode ser nulo: {campo}.",
            )

    if "codigo" in data and data["codigo"] != obj.codigo:
        exists = db.scalar(select(Especialidade).where(Especialidade.codigo == data["codigo"]))
        if exists:
            raise HTTPException(status_code=409, detail="Já existe especialidade com este código.")

    for k, v in data.items():
        setattr(obj, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito de unicidade para código da especialidade.")
    db.refresh(obj)
    return obj


@router.delete("/{especialidade_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(especialidade_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, especialidade_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível remover especialidade com vínculos ativos.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
