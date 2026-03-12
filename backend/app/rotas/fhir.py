import json
from io import BytesIO
from datetime import date, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modelos.paciente import Paciente
from app.modelos.agendamento import Agendamento
from app.modelos.profissional import Profissional
from app.modelos.local_atendimento import LocalAtendimento

from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.agendamento import agendamento_para_fhir
from app.serializadores_fhir.bundle import montar_bundle_agendamento
from app.serializadores_fhir.bundle_geral import (
    build_searchset_bundle,
    build_transaction_bundle,
    validate_bundle_for_hapi_operation,
)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/fhir", tags=["FHIR R4"])


def _fmt_dt_br(dt) -> str:
    if dt is None:
        return "-"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt
    try:
        return dt.astimezone().strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt)


def _safe(v) -> str:
    return "-" if v is None else str(v)


def _buscar_dados_bundle_geral(
    db: Session,
    include_pacientes: bool,
    include_profissionais: bool,
    include_agendamentos: bool,
    include_locais: bool,
    limit: int,
    offset: int,
    start: date | None,
    end: date | None,
):
    if start and end and start > end:
        raise HTTPException(
            status_code=400,
            detail="Parâmetro start deve ser menor ou igual a end.",
        )

    pacientes = []
    profissionais = []
    agendamentos = []
    locais = []

    if include_pacientes:
        pacientes = db.execute(
            select(Paciente)
            .order_by(Paciente.nome.asc())
            .offset(offset)
            .limit(limit)
        ).scalars().all()

    if include_profissionais:
        profissionais = db.execute(
            select(Profissional)
            .order_by(Profissional.nome.asc())
            .offset(offset)
            .limit(limit)
        ).scalars().all()

    if include_agendamentos:
        stmt_agendamentos = (
            select(Agendamento)
            .options(
                joinedload(Agendamento.paciente),
                joinedload(Agendamento.profissional),
                joinedload(Agendamento.especialidade),
                joinedload(Agendamento.local),
            )
            .order_by(Agendamento.inicio.desc())
        )
        if start:
            stmt_agendamentos = stmt_agendamentos.where(
                Agendamento.inicio >= datetime.combine(start, time.min)
            )
        if end:
            stmt_agendamentos = stmt_agendamentos.where(
                Agendamento.inicio <= datetime.combine(end, time.max)
            )
        agendamentos = db.execute(
            stmt_agendamentos.offset(offset).limit(limit)
        ).scalars().all()

    if include_locais:
        locais = db.execute(
            select(LocalAtendimento)
            .order_by(LocalAtendimento.nome.asc())
            .offset(offset)
            .limit(limit)
        ).scalars().all()

    return pacientes, profissionais, agendamentos, locais


def _build_filtered_searchset_bundle(
    db: Session,
    include_pacientes: bool,
    include_profissionais: bool,
    include_agendamentos: bool,
    include_locais: bool,
    limit: int,
    offset: int,
    start: date | None,
    end: date | None,
):
    pacientes, profissionais, agendamentos, locais = _buscar_dados_bundle_geral(
        db=db,
        include_pacientes=include_pacientes,
        include_profissionais=include_profissionais,
        include_agendamentos=include_agendamentos,
        include_locais=include_locais,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )
    try:
        return build_searchset_bundle(
            pacientes=pacientes,
            profissionais=profissionais,
            agendamentos=agendamentos,
            locais=locais,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _build_filtered_transaction_bundle(
    db: Session,
    include_pacientes: bool,
    include_profissionais: bool,
    include_agendamentos: bool,
    include_locais: bool,
    limit: int,
    offset: int,
    start: date | None,
    end: date | None,
):
    pacientes, profissionais, agendamentos, locais = _buscar_dados_bundle_geral(
        db=db,
        include_pacientes=include_pacientes,
        include_profissionais=include_profissionais,
        include_agendamentos=include_agendamentos,
        include_locais=include_locais,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )
    try:
        bundle = build_transaction_bundle(
            pacientes=pacientes,
            profissionais=profissionais,
            agendamentos=agendamentos,
            locais=locais,
        )
        # Guarda técnica: payload destinado a POST no HAPI deve ser transacional.
        validate_bundle_for_hapi_operation(
            bundle=bundle,
            operation="post_transaction",
        )
        return bundle
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def gerar_pdf_bundle_geral(bundle: dict) -> bytes:
    texto = json.dumps(bundle, ensure_ascii=False, indent=2)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _, height = A4

    margem_esquerda = 36
    margem_superior = height - 40
    margem_inferior = 35
    altura_linha = 10
    y = margem_superior

    c.setTitle("Bundle Geral FHIR")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margem_esquerda, y, "Bundle Geral FHIR (searchset)")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(
        margem_esquerda,
        y,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
    )
    y -= 14
    c.setFont("Courier", 8)

    for linha in texto.splitlines():
        partes = [linha[i : i + 118] for i in range(0, len(linha), 118)] or [""]
        for parte in partes:
            if y <= margem_inferior:
                c.showPage()
                y = margem_superior
                c.setFont("Courier", 8)
            c.drawString(margem_esquerda, y, parte)
            y -= altura_linha

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def gerar_pdf_comprovante(a: Agendamento) -> bytes:
    p = a.paciente
    prof = a.profissional
    loc = a.local
    esp = a.especialidade
    usuario = getattr(a, "criado_por", None)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 60

    c.setTitle(f"Comprovante - Agendamento #{a.id}")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Comprovante de Agendamento (UBS)")
    y -= 25

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 18

    c.setLineWidth(1)
    c.line(50, y, width - 50, y)
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Dados do paciente")
    y -= 16
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Nome: {_safe(getattr(p, 'nome', None))}")
    y -= 14
    c.drawString(50, y, f"CNS: {_safe(getattr(p, 'cartao_sus', None))}")
    y -= 14
    c.drawString(50, y, f"Data de nascimento: {_safe(str(getattr(p, 'data_nascimento', '-'))[:10])}")
    y -= 14
    c.drawString(50, y, f"Telefone: {_safe(getattr(p, 'telefone', None))}")
    y -= 14
    c.drawString(50, y, f"Município: {_safe(getattr(p, 'municipio', None))}")
    y -= 14
    c.drawString(50, y, f"Endereço: {_safe(getattr(p, 'endereco', None))}")
    y -= 14
    c.drawString(50, y, f"Nome da mãe: {_safe(getattr(p, 'nome_mae', None))}")
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Dados do atendimento")
    y -= 16
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Nº do agendamento: #{_safe(getattr(a, 'id', None))}")
    y -= 14
    c.drawString(50, y, f"Data/Hora: {_fmt_dt_br(getattr(a, 'inicio', None))}")
    y -= 14
    c.drawString(50, y, f"Especialidade: {_safe(getattr(esp, 'nome', None))}")
    y -= 14

    crm_str = ""
    if getattr(prof, "crm", None) and getattr(prof, "crm_uf", None):
        crm_str = f" (CRM {prof.crm}-{prof.crm_uf})"

    c.drawString(50, y, f"Profissional: {_safe(getattr(prof, 'nome', None))}{crm_str}")
    y -= 14
    c.drawString(50, y, f"Local: {_safe(getattr(loc, 'nome', None))}")
    y -= 14
    c.drawString(50, y, f"Endereço do local: {_safe(getattr(loc, 'endereco', None))}")
    y -= 14
    c.drawString(50, y, f"Modalidade: {_safe(getattr(a, 'modalidade', None))}")
    y -= 14
    c.drawString(50, y, f"Status: {_safe(getattr(a, 'status', None))}")
    y -= 14

    if usuario:
        c.drawString(50, y, f"Agendado por: {_safe(getattr(usuario, 'nome', None))}")
        y -= 14

    y -= 10
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Orientações: chegue com 15 minutos de antecedência (se presencial).")
    y -= 12
    c.drawString(50, y, "Em caso de dúvidas, procure a recepção da unidade.")
    y -= 20

    c.setLineWidth(1)
    c.line(50, 80, width - 50, 80)
    c.setFont("Helvetica", 9)
    c.drawString(50, 65, "Este documento é um comprovante de agendamento e pode ser impresso.")
    c.drawString(50, 52, "Sistema de Agendamento UBS (Projeto PET)")

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


@router.get("/patient/{paciente_id}")
def get_patient_fhir(
    paciente_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    p = db.get(Paciente, paciente_id)
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    try:
        resource = paciente_para_fhir(p)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return JSONResponse(content=resource, media_type="application/fhir+json")


@router.get("/practitioner/{profissional_id}")
def get_practitioner_fhir(
    profissional_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    prof = db.get(Profissional, profissional_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")
    try:
        resource = profissional_para_fhir(prof)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return JSONResponse(content=resource, media_type="application/fhir+json")


@router.get("/location/{local_id}")
def get_location_fhir(
    local_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    loc = db.get(LocalAtendimento, local_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    try:
        resource = local_para_fhir(loc)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return JSONResponse(content=resource, media_type="application/fhir+json")


@router.get("/appointment/{agendamento_id}")
def get_appointment_fhir(
    agendamento_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    a = db.get(Agendamento, agendamento_id)
    if not a:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    _ = a.paciente, a.profissional, a.especialidade, a.local

    try:
        resource = agendamento_para_fhir(a)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return JSONResponse(content=resource, media_type="application/fhir+json")


@router.get("/bundle/agendamento/{id}")
def get_agendamento_bundle_fhir(
    id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    stmt = (
        select(Agendamento)
        .options(
            joinedload(Agendamento.paciente),
            joinedload(Agendamento.profissional),
            joinedload(Agendamento.local),
            joinedload(Agendamento.especialidade),
        )
        .where(Agendamento.id == id)
    )
    a = db.execute(stmt).scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    try:
        bundle = montar_bundle_agendamento(a)
        # Evita regressão estrutural no bundle transacional individual.
        validate_bundle_for_hapi_operation(
            bundle=bundle,
            operation="post_transaction",
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return JSONResponse(content=bundle, media_type="application/fhir+json")


@router.get("/bundle/geral")
@router.get("/bundle/geral/searchset")
def get_bundle_geral_searchset_fhir(
    include_pacientes: bool = Query(default=True),
    include_profissionais: bool = Query(default=True),
    include_agendamentos: bool = Query(default=True),
    include_locais: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    bundle = _build_filtered_searchset_bundle(
        db=db,
        include_pacientes=include_pacientes,
        include_profissionais=include_profissionais,
        include_agendamentos=include_agendamentos,
        include_locais=include_locais,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )

    return JSONResponse(
        content=bundle,
        media_type="application/fhir+json",
        headers={"X-FHIR-Bundle-Purpose": "searchset-listing-only"},
    )


@router.get("/bundle/geral/transaction")
def get_bundle_geral_transaction_fhir(
    include_pacientes: bool = Query(default=True),
    include_profissionais: bool = Query(default=True),
    include_agendamentos: bool = Query(default=True),
    include_locais: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    bundle = _build_filtered_transaction_bundle(
        db=db,
        include_pacientes=include_pacientes,
        include_profissionais=include_profissionais,
        include_agendamentos=include_agendamentos,
        include_locais=include_locais,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )

    return JSONResponse(content=bundle, media_type="application/fhir+json")


@router.get("/bundle/geral/pdf")
def get_bundle_geral_pdf(
    include_pacientes: bool = Query(default=True),
    include_profissionais: bool = Query(default=True),
    include_agendamentos: bool = Query(default=True),
    include_locais: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    bundle = _build_filtered_searchset_bundle(
        db=db,
        include_pacientes=include_pacientes,
        include_profissionais=include_profissionais,
        include_agendamentos=include_agendamentos,
        include_locais=include_locais,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )

    pdf_bytes = gerar_pdf_bundle_geral(bundle)
    headers = {"Content-Disposition": 'inline; filename="bundle_geral_fhir.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/bundle/comprovante/{agendamento_id}")
def get_comprovante_pdf(
    agendamento_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    a = db.get(Agendamento, agendamento_id)
    if not a:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    _ = a.paciente, a.profissional, a.local, a.especialidade
    if not all([a.paciente, a.profissional, a.local, a.especialidade]):
        raise HTTPException(
            status_code=409,
            detail="Dados relacionados incompletos para gerar comprovante.",
        )

    pdf_bytes = gerar_pdf_comprovante(a)
    filename = f"comprovante_agendamento_{a.id}.pdf"
    headers = {"Content-Disposition": f'inline; filename="{filename}"'}

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
