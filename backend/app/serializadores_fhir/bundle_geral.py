import logging
import uuid
from urllib.parse import urlparse

from app.serializadores_fhir.agendamento import agendamento_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir
from app.serializadores_fhir.utils import clean_fhir

logger = logging.getLogger(__name__)


class BundleValidationError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _fail_validation(code: str, message: str, **context) -> None:
    logger.warning(
        "FHIR bundle validation failed: %s - %s | context=%s",
        code,
        message,
        context,
    )
    raise BundleValidationError(code=code, message=message)


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


def _uuid_from_rest_ref(rest_ref: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, rest_ref))


def _urn_from_rest_ref(rest_ref: str) -> str:
    return f"urn:uuid:{_uuid_from_rest_ref(rest_ref)}"


def _entry_transacao(resource: dict, rest_to_urn: dict[str, str]) -> dict:
    if not isinstance(resource, dict):
        raise ValueError("Recurso FHIR inválido para entrada de transação.")

    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")
    if not resource_type or resource_id is None:
        raise ValueError("Recurso FHIR sem resourceType/id para Bundle transaction.")

    resource_id = str(resource_id)
    rest_ref = f"{resource_type}/{resource_id}"
    urn_ref = rest_to_urn.setdefault(rest_ref, _urn_from_rest_ref(rest_ref))
    urn_id = urn_ref.replace("urn:uuid:", "", 1)

    # Para HAPI local: POST + urn:uuid consistente evita erro com ids numéricos.
    resource_with_uuid = dict(resource)
    resource_with_uuid["id"] = urn_id
    return {
        "fullUrl": urn_ref,
        "resource": resource_with_uuid,
        "request": {
            "method": "POST",
            "url": resource_type,
        },
    }


def _normalizar_referencia_rest(reference: str) -> str:
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("Reference inválida em Appointment.participant.actor.")

    ref = reference.strip()
    if ref.startswith("urn:uuid:"):
        raise ValueError(
            "Bundle transaction usa referências REST (ResourceType/id), não urn:uuid."
        )

    if "://" in ref:
        parsed = urlparse(ref)
        ref = parsed.path or ref

    ref = ref.split("/_history/")[0].strip("/")
    parts = ref.split("/")
    if len(parts) < 2:
        raise ValueError(
            "Reference inválida em Appointment.participant.actor. "
            "Use o formato ResourceType/id."
        )

    return f"{parts[-2]}/{parts[-1]}"


def _normalizar_referencias_appointment(
    resource: dict,
    rest_to_urn: dict[str, str],
) -> None:
    if resource.get("resourceType") != "Appointment":
        return

    for participant in resource.get("participant", []):
        if not isinstance(participant, dict):
            continue
        actor = participant.get("actor")
        if not isinstance(actor, dict):
            continue
        reference = actor.get("reference")
        if not isinstance(reference, str) or not reference.strip():
            continue
        if reference.startswith("urn:uuid:"):
            actor["reference"] = reference
            continue

        rest_ref = _normalizar_referencia_rest(reference)
        urn_ref = rest_to_urn.get(rest_ref)
        if not urn_ref:
            raise ValueError(
                f"Reference {rest_ref} não encontrada no bundle transaction."
            )
        actor["reference"] = urn_ref


def _validar_referencias_appointment_no_bundle(
    resource: dict,
    full_urls: set[str],
) -> None:
    if resource.get("resourceType") != "Appointment":
        return

    for participant in resource.get("participant", []):
        if not isinstance(participant, dict):
            continue
        actor = participant.get("actor")
        if not isinstance(actor, dict):
            continue
        reference = actor.get("reference")
        if not isinstance(reference, str):
            continue
        if reference.startswith("urn:uuid:"):
            if reference not in full_urls:
                raise ValueError(
                    f"Reference {reference} não encontrada no bundle transaction."
                )
            continue

        rest_ref = _normalizar_referencia_rest(reference)
        if rest_ref.startswith(("Patient/", "Practitioner/", "Location/")):
            raise ValueError(
                f"Reference {rest_ref} inválida para bundle transaction HAPI. "
                "Use referências internas no formato urn:uuid."
            )


def _entries_para_recursos(itens, serializer):
    entries = []
    for item in (itens or []):
        resource = serializer(item)
        entries.append(_entry_searchset(resource))
    return entries


def _entries_para_transacao(itens, serializer, rest_to_urn: dict[str, str]):
    entries = []
    for item in (itens or []):
        resource = serializer(item)
        entries.append(_entry_transacao(resource, rest_to_urn))
    return entries


def build_searchset_bundle(pacientes, profissionais, agendamentos, locais):
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


def build_transaction_bundle(pacientes, profissionais, agendamentos, locais):
    # Para importação no HAPI: transaction com request.method/request.url em cada entry.
    rest_to_urn: dict[str, str] = {}
    entry = []
    entry.extend(_entries_para_transacao(pacientes, paciente_para_fhir, rest_to_urn))
    entry.extend(
        _entries_para_transacao(profissionais, profissional_para_fhir, rest_to_urn)
    )
    entry.extend(_entries_para_transacao(locais, local_para_fhir, rest_to_urn))
    entry.extend(
        _entries_para_transacao(agendamentos, agendamento_para_fhir, rest_to_urn)
    )

    full_urls = {
        item.get("fullUrl")
        for item in entry
        if isinstance(item, dict) and isinstance(item.get("fullUrl"), str)
    }

    for item in entry:
        resource = item.get("resource")
        if isinstance(resource, dict):
            _normalizar_referencias_appointment(resource, rest_to_urn)
            _validar_referencias_appointment_no_bundle(resource, full_urls)

    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": entry,
    }

    return clean_fhir(bundle)


def build_patient_appointments_transaction_bundle(
    paciente,
    profissionais,
    agendamentos,
    locais,
):
    paciente_id = getattr(paciente, "id", None)
    if paciente is None or paciente_id is None:
        raise ValueError(
            "Paciente obrigatório para montar bundle transacional de agendamentos."
        )

    # Cenário alvo: 1 paciente + N profissionais + N locais + N agendamentos.
    bundle = build_transaction_bundle(
        pacientes=[paciente],
        profissionais=profissionais,
        agendamentos=agendamentos,
        locais=locais,
    )

    ref_paciente_urn = None
    for entry in bundle.get("entry", []):
        resource = entry.get("resource")
        if not isinstance(resource, dict):
            continue
        if resource.get("resourceType") != "Patient":
            continue
        full_url = entry.get("fullUrl")
        if isinstance(full_url, str) and full_url.startswith("urn:uuid:"):
            ref_paciente_urn = full_url
            break

    if not ref_paciente_urn:
        raise ValueError("Paciente principal não encontrado no bundle transaction.")

    for entry in bundle.get("entry", []):
        resource = entry.get("resource")
        if not isinstance(resource, dict):
            continue
        if resource.get("resourceType") != "Appointment":
            continue

        refs_participantes = set()
        for participant in resource.get("participant", []):
            if not isinstance(participant, dict):
                continue
            actor = participant.get("actor")
            if not isinstance(actor, dict):
                continue
            reference = actor.get("reference")
            if not isinstance(reference, str):
                continue
            refs_participantes.add(reference)

        if ref_paciente_urn not in refs_participantes:
            raise ValueError(
                "Appointment com referência de paciente inconsistente "
                "com o paciente principal do bundle."
            )

    validate_bundle_for_hapi_operation(
        bundle=bundle,
        operation="post_transaction",
    )
    return bundle


def validate_bundle_for_hapi_post(bundle: dict) -> None:
    validate_bundle_for_hapi_operation(bundle=bundle, operation="post")


def validate_bundle_for_hapi_operation(bundle: dict, operation: str) -> None:
    allowed_types_by_operation = {
        "post": {"transaction", "batch"},
        "post_transaction": {"transaction"},
        "post_batch": {"batch"},
    }
    allowed_types = allowed_types_by_operation.get(operation)
    if allowed_types is None:
        _fail_validation(
            code="FHIR_BUNDLE_OPERATION_INVALID",
            message=f"Operação inválida para validação de Bundle: {operation!r}.",
            operation=operation,
        )

    if not isinstance(bundle, dict):
        _fail_validation(
            code="FHIR_BUNDLE_PAYLOAD_INVALID",
            message="Payload inválido: esperado objeto Bundle.",
            operation=operation,
            payload_type=type(bundle).__name__,
        )

    if bundle.get("resourceType") != "Bundle":
        _fail_validation(
            code="FHIR_BUNDLE_RESOURCE_TYPE_INVALID",
            message="Payload inválido: resourceType deve ser 'Bundle'.",
            operation=operation,
            resource_type=bundle.get("resourceType"),
        )

    bundle_type = bundle.get("type")
    if bundle_type not in allowed_types:
        allowed_types_list = ", ".join(sorted(allowed_types))
        if bundle_type == "searchset":
            _fail_validation(
                code="FHIR_BUNDLE_SEARCHSET_NOT_ALLOWED",
                message=(
                    f"Bundle.type='searchset' não pode ser enviado no destino {operation}. "
                    f"Use: {allowed_types_list}."
                ),
                operation=operation,
                bundle_type=bundle_type,
                allowed_types=allowed_types_list,
            )
        _fail_validation(
            code="FHIR_BUNDLE_TYPE_INVALID",
            message=(
                f"Bundle.type incompatível para {operation}: {bundle_type!r}. "
                f"Permitido: {allowed_types_list}."
            ),
            operation=operation,
            bundle_type=bundle_type,
            allowed_types=allowed_types_list,
        )

    entries = bundle.get("entry")
    if not isinstance(entries, list) or len(entries) == 0:
        _fail_validation(
            code="FHIR_BUNDLE_ENTRY_MISSING",
            message="Bundle sem entry para processamento no HAPI.",
            operation=operation,
            bundle_type=bundle_type,
        )

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_INVALID",
                message=f"entry[{i}] inválida: esperado objeto.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )
        if not isinstance(entry.get("resource"), dict):
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_RESOURCE_INVALID",
                message=f"entry[{i}] inválida: resource ausente ou inválido.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )

        request = entry.get("request")
        if not isinstance(request, dict):
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_REQUEST_MISSING",
                message=f"entry[{i}] inválida para {bundle_type}: request ausente.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )
        method = request.get("method")
        url = request.get("url")
        if not isinstance(method, str) or not method.strip():
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_REQUEST_METHOD_MISSING",
                message=f"entry[{i}] inválida: request.method ausente.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )
        method_upper = method.strip().upper()
        if not isinstance(url, str) or not url.strip():
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_REQUEST_URL_MISSING",
                message=f"entry[{i}] inválida: request.url ausente.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )
        url_clean = url.strip().strip("/")

        if operation == "post_transaction" and method_upper == "POST" and "/" in url_clean:
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_POST_URL_INVALID",
                message=(
                    f"entry[{i}] inválida: request.url para POST deve ser apenas o "
                    "ResourceType (sem '/id')."
                ),
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
                request_url=url,
            )

        if operation == "post_transaction" and method_upper == "PUT":
            parts = url_clean.split("/")
            if len(parts) == 2 and parts[1].isdigit():
                _fail_validation(
                    code="FHIR_BUNDLE_ENTRY_NUMERIC_ID_NOT_ALLOWED",
                    message=(
                        f"entry[{i}] inválida para HAPI local: PUT com id numérico "
                        f"({parts[1]!r}) tende a ser rejeitado. "
                        "Use POST + urn:uuid, ou um id alfanumérico."
                    ),
                    operation=operation,
                    bundle_type=bundle_type,
                    entry_index=i,
                    request_url=url,
                )

        if "search" in entry:
            _fail_validation(
                code="FHIR_BUNDLE_ENTRY_SEARCH_NOT_ALLOWED",
                message=f"entry[{i}] inválida para POST no HAPI: campo 'search' não permitido.",
                operation=operation,
                bundle_type=bundle_type,
                entry_index=i,
            )


# Compatibilidade retroativa com chamadas existentes.
def montar_bundle_geral(pacientes, profissionais, agendamentos, locais):
    return build_searchset_bundle(pacientes, profissionais, agendamentos, locais)


def montar_bundle_geral_transacao(pacientes, profissionais, agendamentos, locais):
    return build_transaction_bundle(pacientes, profissionais, agendamentos, locais)
