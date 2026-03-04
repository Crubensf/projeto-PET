from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

# Permite rodar com: python backend/scripts/test_bundle.py (a partir da raiz)
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.core.database import SessionLocal
from app.modelos.agendamento import Agendamento
from app.serializadores_fhir.bundle import montar_bundle_agendamento


class ValidacaoErro(Exception):
    pass


def _assert(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise ValidacaoErro(mensagem)


def _buscar_primeiro_agendamento(db) -> Agendamento | None:
    stmt = (
        select(Agendamento)
        .options(
            joinedload(Agendamento.paciente),
            joinedload(Agendamento.profissional),
            joinedload(Agendamento.local),
            joinedload(Agendamento.especialidade),
        )
        .order_by(Agendamento.id.asc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def _validar_sem_none(obj: Any, caminho: str = "root") -> None:
    if obj is None:
        raise ValidacaoErro(f"None encontrado em: {caminho}")

    if isinstance(obj, dict):
        for chave, valor in obj.items():
            _validar_sem_none(valor, f"{caminho}.{chave}")
        return

    if isinstance(obj, list):
        for i, item in enumerate(obj):
            _validar_sem_none(item, f"{caminho}[{i}]")


def _validar_bundle(bundle: dict[str, Any]) -> None:
    _assert(bundle.get("resourceType") == "Bundle", "bundle.resourceType != 'Bundle'")
    _assert(bundle.get("type") == "transaction", "bundle.type != 'transaction'")

    entries = bundle.get("entry")
    _assert(isinstance(entries, list), "bundle.entry não é lista")
    _assert(len(entries) == 4, f"len(bundle.entry) esperado 4, recebido {len(entries)}")

    for i, entry in enumerate(entries):
        _assert(isinstance(entry, dict), f"entry[{i}] não é objeto")
        _assert("fullUrl" in entry, f"entry[{i}] sem fullUrl")
        _assert("request" in entry, f"entry[{i}] sem request")
        _assert("resource" in entry, f"entry[{i}] sem resource")

    appointment = next(
        (e.get("resource") for e in entries if isinstance(e.get("resource"), dict) and e["resource"].get("resourceType") == "Appointment"),
        None,
    )
    _assert(appointment is not None, "Appointment não encontrado no bundle.entry")

    participantes = appointment.get("participant", [])
    _assert(isinstance(participantes, list), "Appointment.participant não é lista")

    for i, part in enumerate(participantes):
        referencia = part.get("actor", {}).get("reference")
        _assert(
            isinstance(referencia, str) and referencia.startswith("urn:uuid:"),
            f"Appointment.participant[{i}].actor.reference inválido: {referencia!r}",
        )

    _validar_sem_none(bundle)


def main() -> int:
    db = SessionLocal()
    try:
        agendamento = _buscar_primeiro_agendamento(db)
        _assert(agendamento is not None, "Nenhum agendamento encontrado no banco")

        bundle = montar_bundle_agendamento(agendamento)
        _validar_bundle(bundle)

        print("OK")
        return 0
    except ValidacaoErro as erro:
        print(f"ERRO: {erro}")
        return 1
    except Exception as erro:  # fallback para falhas inesperadas
        print(f"ERRO INESPERADO: {erro}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
