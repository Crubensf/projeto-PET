from __future__ import annotations

from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modelos.agendamento import Agendamento
from app.modelos.especialidade import Especialidade
from app.modelos.local_atendimento import LocalAtendimento
from app.modelos.paciente import Paciente
from app.modelos.profissional import Profissional

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


@router.get("/resumo")
def resumo(db: Session = Depends(get_db)):
    """
    Métricas principais para cards.
    """
    total_pacientes = db.scalar(select(func.count()).select_from(Paciente)) or 0
    total_profissionais = db.scalar(select(func.count()).select_from(Profissional)) or 0
    total_especialidades = db.scalar(select(func.count()).select_from(Especialidade)) or 0
    total_locais = db.scalar(select(func.count()).select_from(LocalAtendimento)) or 0
    total_agendamentos = db.scalar(select(func.count()).select_from(Agendamento)) or 0

    hoje = date.today()
    inicio_hoje = datetime.combine(hoje, time.min)
    fim_hoje = datetime.combine(hoje, time.max)

    agendamentos_hoje = (
        db.scalar(
            select(func.count())
            .select_from(Agendamento)
            .where(Agendamento.inicio >= inicio_hoje, Agendamento.inicio <= fim_hoje)
        )
        or 0
    )

    return {
        "total_pacientes": total_pacientes,
        "total_profissionais": total_profissionais,
        "total_especialidades": total_especialidades,
        "total_locais": total_locais,
        "total_agendamentos": total_agendamentos,
        "agendamentos_hoje": agendamentos_hoje,
    }


@router.get("/proximos")
def proximos(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Lista dos próximos agendamentos com informações para tabela do dashboard.
    (join simples para o front não ter que cruzar ids)
    """
    now = datetime.now()

    stmt = (
        select(
            Agendamento.id,
            Agendamento.inicio,
            Agendamento.modalidade,
            Paciente.nome.label("paciente_nome"),
            Profissional.nome.label("profissional_nome"),
            Especialidade.nome.label("especialidade_nome"),
            LocalAtendimento.nome.label("local_nome"),
        )
        .join(Paciente, Paciente.id == Agendamento.paciente_id)
        .join(Profissional, Profissional.id == Agendamento.profissional_id)
        .join(Especialidade, Especialidade.id == Agendamento.especialidade_id)
        .join(LocalAtendimento, LocalAtendimento.id == Agendamento.local_id)
        .where(Agendamento.inicio >= now)
        .order_by(Agendamento.inicio.asc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()
    return [
        {
            "id": r.id,
            "inicio": r.inicio,
            "modalidade": r.modalidade,
            "paciente_nome": r.paciente_nome,
            "profissional_nome": r.profissional_nome,
            "especialidade_nome": r.especialidade_nome,
            "local_nome": r.local_nome,
        }
        for r in rows
    ]


@router.get("/agendamentos/por-dia")
def agendamentos_por_dia(
    start: str = Query(default=None, description="YYYY-MM-DD"),
    end: str = Query(default=None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    Série diária de agendamentos.
    Retorna todos os dias no intervalo (incluindo dias com 0), para o gráfico não ficar 'furado'.
    """
    hoje = date.today()
    start_date = _parse_date(start) if start else (hoje - timedelta(days=6))
    end_date = _parse_date(end) if end else hoje

    if end_date < start_date:
        start_date, end_date = end_date, start_date

    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)

    # Agrupa por data (usa DATE(inicio))
    stmt = (
        select(func.date(Agendamento.inicio).label("dia"), func.count().label("total"))
        .where(Agendamento.inicio >= start_dt, Agendamento.inicio <= end_dt)
        .group_by(func.date(Agendamento.inicio))
        .order_by(func.date(Agendamento.inicio))
    )

    rows = db.execute(stmt).all()
    mapa = {str(r.dia): int(r.total) for r in rows}

    # Preenche dias faltando
    out = []
    d = start_date
    while d <= end_date:
        key = d.isoformat()
        out.append({"data": key, "total": mapa.get(key, 0)})
        d += timedelta(days=1)

    return out


@router.get("/agendamentos/por-especialidade")
def agendamentos_por_especialidade(
    start: str = Query(default=None, description="YYYY-MM-DD"),
    end: str = Query(default=None, description="YYYY-MM-DD"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Ranking por especialidade.
    """
    hoje = date.today()
    start_date = _parse_date(start) if start else (hoje - timedelta(days=29))
    end_date = _parse_date(end) if end else hoje

    if end_date < start_date:
        start_date, end_date = end_date, start_date

    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)

    stmt = (
        select(
            Especialidade.nome.label("especialidade"),
            func.count(Agendamento.id).label("total"),
        )
        .join(Especialidade, Especialidade.id == Agendamento.especialidade_id)
        .where(Agendamento.inicio >= start_dt, Agendamento.inicio <= end_dt)
        .group_by(Especialidade.nome)
        .order_by(func.count(Agendamento.id).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()
    return [{"especialidade": r.especialidade, "total": int(r.total)} for r in rows]
