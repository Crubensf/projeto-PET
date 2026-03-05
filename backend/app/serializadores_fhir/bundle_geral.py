from app.serializadores_fhir.agendamento import agendamento_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir
from app.serializadores_fhir.utils import clean_fhir


def _entry_searchset(resource: dict) -> dict:
    if not isinstance(resource, dict):
        raise ValueError("Recurso FHIR inválido para entrada de busca.")

    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")
    if not resource_type or resource_id is None:
        raise ValueError("Recurso FHIR sem resourceType/id para Bundle searchset.")

    return {
        "fullUrl": f"{resource_type}/{resource_id}",
        "resource": resource,
        "search": {"mode": "match"},
    }


def _entries_para_recursos(itens, serializer):
    entries = []
    for item in (itens or []):
        resource = serializer(item)
        entries.append(_entry_searchset(resource))
    return entries


def montar_bundle_geral(pacientes, profissionais, agendamentos, locais):
    entry = []
    entry.extend(_entries_para_recursos(pacientes, paciente_para_fhir))
    entry.extend(_entries_para_recursos(profissionais, profissional_para_fhir))
    entry.extend(_entries_para_recursos(agendamentos, agendamento_para_fhir))
    entry.extend(_entries_para_recursos(locais, local_para_fhir))

    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entry),
        "entry": entry,
    }

    return clean_fhir(bundle)
