from app.serializadores_fhir.agendamento import agendamento_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir


def _entry_transacao(resource: dict) -> dict:
    resource_type = resource["resourceType"]
    resource_id = str(resource["id"])

    return {
        "fullUrl": f"urn:uuid:{resource_id}",
        "resource": resource,
        "request": {
            "method": "PUT",
            "url": f"{resource_type}/{resource_id}",
        },
    }


def montar_bundle_agendamento(a):
    paciente = paciente_para_fhir(a.paciente)
    profissional = profissional_para_fhir(a.profissional)
    local = local_para_fhir(a.local)
    agendamento = agendamento_para_fhir(a)

    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            _entry_transacao(paciente),
            _entry_transacao(profissional),
            _entry_transacao(local),
            _entry_transacao(agendamento),
        ],
    }
