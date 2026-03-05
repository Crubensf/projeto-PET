from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

# Permite rodar com: python3 backend/scripts/test_bundle_geral.py (a partir da raiz)
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.core.bootstrap import bootstrap_all
from app.core.database import SessionLocal
from app.modelos.agendamento import Agendamento
from app.modelos.local_atendimento import LocalAtendimento
from app.modelos.paciente import Paciente
from app.modelos.profissional import Profissional
from app.serializadores_fhir.bundle_geral import montar_bundle_geral


class ValidacaoErro(Exception):
    pass


def _assert(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise ValidacaoErro(mensagem)


def _carregar_pacientes(db):
    return db.execute(
        select(Paciente)
        .order_by(Paciente.nome.asc())
        .limit(3)
    ).scalars().all()


def _carregar_profissionais(db):
    return db.execute(
        select(Profissional)
        .order_by(Profissional.nome.asc())
        .limit(3)
    ).scalars().all()


def _carregar_agendamentos(db):
    return db.execute(
        select(Agendamento)
        .options(
            joinedload(Agendamento.paciente),
            joinedload(Agendamento.profissional),
            joinedload(Agendamento.especialidade),
            joinedload(Agendamento.local),
        )
        .order_by(Agendamento.inicio.desc())
        .limit(3)
    ).scalars().all()


def _carregar_locais(db):
    return db.execute(
        select(LocalAtendimento)
        .order_by(LocalAtendimento.nome.asc())
        .limit(3)
    ).scalars().all()


def _validar_bundle(bundle: dict[str, Any]) -> None:
    _assert(bundle.get("resourceType") == "Bundle", "resourceType inválido")
    _assert(bundle.get("type") == "searchset", "type inválido")

    entry = bundle.get("entry")
    _assert(isinstance(entry, list), "entry ausente ou não é lista")

    total = bundle.get("total")
    _assert(total == len(entry), f"total ({total}) difere de len(entry) ({len(entry)})")

    for i, item in enumerate(entry):
        _assert(isinstance(item, dict), f"entry[{i}] não é objeto")
        resource = item.get("resource")
        _assert(isinstance(resource, dict), f"entry[{i}].resource inválido")
        resource_type = resource.get("resourceType")
        _assert(
            isinstance(resource_type, str) and resource_type.strip() != "",
            f"entry[{i}].resource.resourceType ausente",
        )


def main() -> int:
    db = None
    try:
        bootstrap_all()
        db = SessionLocal()

        pacientes = _carregar_pacientes(db)
        profissionais = _carregar_profissionais(db)
        agendamentos = _carregar_agendamentos(db)
        locais = _carregar_locais(db)

        bundle = montar_bundle_geral(
            pacientes=pacientes,
            profissionais=profissionais,
            agendamentos=agendamentos,
            locais=locais,
        )

        _validar_bundle(bundle)
        print("OK")
        return 0
    except ValidacaoErro as erro:
        print(f"ERRO: {erro}")
        return 1
    except Exception as erro:
        print(f"ERRO INESPERADO: {erro}")
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
