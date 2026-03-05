import uuid

from app.serializadores_fhir.agendamento import agendamento_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir
from app.serializadores_fhir.utils import clean_fhir


def _urn_por_recurso(resource_type: str, resource_id: str) -> str:
    value = uuid.uuid5(uuid.NAMESPACE_URL, f"{resource_type}/{resource_id}")
    return f"urn:uuid:{value}"


def _entry_transacao(resource: dict) -> dict:
    if not isinstance(resource, dict):
        raise ValueError("Recurso FHIR inválido para entrada de transação.")

    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")
    if not resource_type or resource_id is None:
        raise ValueError("Recurso FHIR sem resourceType/id para transação.")

    resource_id = str(resource_id)
    full_url = _urn_por_recurso(resource_type, resource_id)

    return {
        "fullUrl": full_url,
        "resource": resource,
        "request": {
            "method": "PUT",
            "url": f"{resource_type}/{resource_id}",
        },
    }


def montar_bundle_agendamento(a):
    if not all([a.paciente, a.profissional, a.local, a.especialidade]):
        raise ValueError("Agendamento sem relacionamentos obrigatórios para gerar Bundle.")

    paciente = paciente_para_fhir(a.paciente)
    profissional = profissional_para_fhir(a.profissional)
    local = local_para_fhir(a.local)
    agendamento = agendamento_para_fhir(a)

    paciente_id = paciente.get("id")
    profissional_id = profissional.get("id")
    local_id = local.get("id")
    if paciente_id is None or profissional_id is None or local_id is None:
        raise ValueError("Recursos relacionados sem id para gerar Bundle.")

    refs_urn = {
        f"Patient/{paciente_id}": _urn_por_recurso("Patient", str(paciente_id)),
        f"Practitioner/{profissional_id}": _urn_por_recurso("Practitioner", str(profissional_id)),
        f"Location/{local_id}": _urn_por_recurso("Location", str(local_id)),
    }
    for participant in agendamento.get("participant", []):
        if not isinstance(participant, dict):
            continue
        actor = participant.get("actor")
        if not isinstance(actor, dict):
            continue
        referencia = actor.get("reference")
        if referencia in refs_urn:
            actor["reference"] = refs_urn[referencia]

    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            _entry_transacao(paciente),
            _entry_transacao(profissional),
            _entry_transacao(local),
            _entry_transacao(agendamento),
        ],
    }

    return clean_fhir(bundle)
