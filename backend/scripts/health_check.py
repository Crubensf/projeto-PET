from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import joinedload

# Permite rodar com: python backend/scripts/health_check.py (a partir da raiz)
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.core.bootstrap import bootstrap_all
from app.core.database import SessionLocal
from app.modelos.agendamento import Agendamento
from app.modelos.paciente import Paciente
from app.modelos.profissional import Profissional
from app.serializadores_fhir.bundle import montar_bundle_agendamento


class HealthCheckError(Exception):
    pass


def _fail(msg: str) -> None:
    raise HealthCheckError(msg)


def main() -> int:
    db = None
    try:
        bootstrap_all()

        db = SessionLocal()

        paciente = db.execute(
            select(Paciente).order_by(Paciente.id.asc()).limit(1)
        ).scalar_one_or_none()
        if paciente is None:
            _fail("falha ao buscar paciente: nenhum registro encontrado")

        profissional = db.execute(
            select(Profissional).order_by(Profissional.id.asc()).limit(1)
        ).scalar_one_or_none()
        if profissional is None:
            _fail("falha ao buscar profissional: nenhum registro encontrado")

        agendamento = db.execute(
            select(Agendamento)
            .options(
                joinedload(Agendamento.paciente),
                joinedload(Agendamento.profissional),
                joinedload(Agendamento.local),
                joinedload(Agendamento.especialidade),
            )
            .order_by(Agendamento.id.asc())
            .limit(1)
        ).scalar_one_or_none()
        if agendamento is None:
            _fail("falha ao buscar agendamento: nenhum registro encontrado")

        bundle = montar_bundle_agendamento(agendamento)

        if not isinstance(bundle, dict):
            _fail("falha ao gerar bundle: retorno não é objeto JSON")

        if bundle.get("resourceType") != "Bundle":
            _fail("bundle.resourceType inválido")

        if bundle.get("type") != "transaction":
            _fail("bundle.type inválido")

        entries = bundle.get("entry")
        if not isinstance(entries, list):
            _fail("bundle.entry inválido")

        resource_types = set()
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                _fail(f"bundle.entry[{i}] inválido")

            resource = entry.get("resource")
            if not isinstance(resource, dict):
                _fail(f"bundle.entry[{i}].resource inválido")

            rt = resource.get("resourceType")
            if not isinstance(rt, str) or not rt:
                _fail(f"bundle.entry[{i}].resource.resourceType inválido")

            resource_types.add(rt)

        required = {"Patient", "Practitioner", "Location", "Appointment"}
        missing = sorted(required - resource_types)
        if missing:
            _fail(f"bundle.entry sem recursos obrigatórios: {', '.join(missing)}")

        print("OK")
        return 0

    except HealthCheckError as exc:
        print(f"ERRO: {exc}")
        return 1
    except Exception as exc:  # fallback para erros inesperados
        print(f"ERRO: falha inesperada: {exc}")
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
