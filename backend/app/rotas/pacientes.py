from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.validators import (
    is_valid_cns,
    is_valid_cpf,
    is_valid_phone,
    sanitize_cns,
    sanitize_cpf,
    sanitize_phone,
)
from app.modelos.paciente import Paciente
from app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate


router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(get_current_user)],
)

def _paciente_invalido(p: Paciente) -> bool:
    return (
        not is_valid_cpf(getattr(p, "cpf", None))
        or not is_valid_cns(p.cartao_sus)
        or not is_valid_phone(p.telefone)
    )


def _assert_paciente_consistente(p: Paciente) -> None:
    if _paciente_invalido(p):
        raise HTTPException(
            status_code=500,
            detail=(
                f"Registro de paciente inválido (id={p.id}). "
                "Corrija CPF (11 dígitos), CNS (15 dígitos) e telefone (10-11)."
            ),
        )


@router.get("/by-cns/{cns}", response_model=PacienteOut)
def buscar_por_cns(cns: str, db: Session = Depends(get_db)):
    try:
        cns_digits = sanitize_cns(cns)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="CNS deve ter exatamente 15 dígitos.",
        )

    obj = db.scalar(select(Paciente).where(Paciente.cartao_sus == cns_digits))
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    _assert_paciente_consistente(obj)
    return obj


@router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def criar(payload: PacienteCreate, db: Session = Depends(get_db)):
    try:
        cpf_digits = sanitize_cpf(payload.cpf)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="CPF deve conter exatamente 11 dígitos.",
        )

    # CPF único
    exists_cpf = db.scalar(
        select(Paciente).where(Paciente.cpf == cpf_digits)
    )
    if exists_cpf:
        raise HTTPException(
            status_code=409,
            detail="Já existe paciente com este CPF.",
        )

    try:
        cns_digits = sanitize_cns(payload.cartao_sus)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="CNS deve conter exatamente 15 dígitos.",
        )

    try:
        telefone_digits = sanitize_phone(payload.telefone)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Telefone deve ter 10 ou 11 dígitos.",
        )

    exists_cns = db.scalar(
        select(Paciente).where(Paciente.cartao_sus == cns_digits)
    )
    if exists_cns:
        raise HTTPException(
            status_code=409,
            detail="Já existe paciente com este cartão SUS.",
        )

    data = payload.model_dump()
    data["cpf"] = cpf_digits
    data["cartao_sus"] = cns_digits
    data["telefone"] = telefone_digits

    obj = Paciente(**data)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflito de unicidade para CPF/CNS.",
        )
    db.refresh(obj)
    return obj


@router.get("", response_model=list[PacienteOut])
def listar(db: Session = Depends(get_db)):
    rows = list(db.scalars(select(Paciente).order_by(Paciente.nome)).all())

    invalid = [p for p in rows if _paciente_invalido(p)]
    if invalid:
        ids = [p.id for p in invalid][:20]
        raise HTTPException(
            status_code=500,
            detail=(
                f"Base contém pacientes inválidos (ids={ids}). "
                "Corrija CPF (11 dígitos), CNS (15 dígitos) e telefone (10-11)."
            ),
        )

    return rows


@router.get("/{paciente_id}", response_model=PacienteOut)
def detalhar(
    paciente_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    _assert_paciente_consistente(obj)
    return obj


@router.put("/{paciente_id}", response_model=PacienteOut)
def atualizar(
    payload: PacienteUpdate,
    paciente_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado."
        )

    data = payload.model_dump(exclude_unset=True)
    campos_obrigatorios = (
        "nome",
        "cpf",
        "cartao_sus",
        "telefone",
        "data_nascimento",
        "municipio",
        "endereco",
        "nome_mae",
    )
    for campo in campos_obrigatorios:
        if campo in data and data[campo] is None:
            raise HTTPException(
                status_code=422,
                detail=f"Campo obrigatório não pode ser nulo: {campo}.",
            )

    # ---------- CPF ----------
    if "cpf" in data:
        try:
            cpf_digits = sanitize_cpf(data["cpf"])
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="CPF deve conter exatamente 11 dígitos."
            )

        if cpf_digits != obj.cpf:
            exists = db.scalar(
                select(Paciente).where(Paciente.cpf == cpf_digits)
            )
            if exists:
                raise HTTPException(
                    status_code=409,
                    detail="Já existe paciente com este CPF."
                )

        data["cpf"] = cpf_digits

    # ---------- CARTÃO SUS (opcional) ----------
    if "cartao_sus" in data:
        if data["cartao_sus"] in (None, ""):
            raise HTTPException(
                status_code=422,
                detail="CNS não pode ser vazio.",
            )

        try:
            cns_digits = sanitize_cns(data["cartao_sus"])
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="CNS deve conter exatamente 15 dígitos."
            )

        if cns_digits != obj.cartao_sus:
            exists = db.scalar(
                select(Paciente).where(Paciente.cartao_sus == cns_digits)
            )
            if exists:
                raise HTTPException(
                    status_code=409,
                    detail="Já existe paciente com este cartão SUS."
                )

        data["cartao_sus"] = cns_digits

    # ---------- TELEFONE ----------
    if "telefone" in data:
        try:
            tel_digits = sanitize_phone(data["telefone"])
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Telefone deve ter 10 ou 11 dígitos."
            )

        data["telefone"] = tel_digits

    # ---------- ATUALIZA CAMPOS ----------
    for k, v in data.items():
        setattr(obj, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflito de unicidade para CPF/CNS.",
        )
    db.refresh(obj)
    return obj



@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    paciente_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    obj = db.get(Paciente, paciente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    db.delete(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não é possível remover paciente com vínculos ativos.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/by-cpf/{cpf}", response_model=PacienteOut)
def buscar_por_cpf(cpf: str, db: Session = Depends(get_db)):
    try:
        cpf_digits = sanitize_cpf(cpf)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="CPF deve conter exatamente 11 dígitos.",
        )

    obj = db.scalar(select(Paciente).where(Paciente.cpf == cpf_digits))
    if not obj:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    _assert_paciente_consistente(obj)

    return obj
