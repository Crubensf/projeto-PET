from datetime import timedelta


DEFAULT_APPOINTMENT_DURATION_MINUTES = 30


def _to_int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _resolve_duration_minutes(a) -> int:
    # Prioriza duração explícita no agendamento; depois tenta na especialidade.
    candidate_attrs = (
        "duracao_minutos",
        "duracao_consulta_minutos",
        "duracao",
    )
    for attr in candidate_attrs:
        value = _to_int_or_none(getattr(a, attr, None))
        if value and value > 0:
            return value

    especialidade = getattr(a, "especialidade", None)
    if especialidade is not None:
        for attr in candidate_attrs:
            value = _to_int_or_none(getattr(especialidade, attr, None))
            if value and value > 0:
                return value

    return DEFAULT_APPOINTMENT_DURATION_MINUTES


def _resolve_end_datetime(a):
    inicio = getattr(a, "inicio", None)
    if inicio is None:
        return None

    for attr in ("fim", "end"):
        maybe_end = getattr(a, attr, None)
        if maybe_end is not None:
            return maybe_end

    return inicio + timedelta(minutes=_resolve_duration_minutes(a))


def agendamento_para_fhir(a):
    # 🔥 Mapeamento PT → FHIR
    STATUS_MAP = {
        "agendado": "booked",
        "cancelado": "cancelled",
        "atendido": "fulfilled",
    }

    status_pt = (a.status or "agendado").lower()
    status_fhir = STATUS_MAP.get(status_pt, "booked")

    resource = {
        "resourceType": "Appointment",
        "id": str(a.id),
        "status": status_fhir,
        "serviceType": [
            {
                "coding": [
                    {
                        "code": getattr(a.especialidade, "codigo", None),
                        "display": getattr(a.especialidade, "nome", None),
                    }
                ]
            }
        ],
        "participant": [
            {
                "actor": {
                    "reference": f"Patient/{a.paciente_id}",
                    "display": getattr(a.paciente, "nome", None),
                },
                "status": "accepted",
            },
            {
                "actor": {
                    "reference": f"Practitioner/{a.profissional_id}",
                    "display": getattr(a.profissional, "nome", None),
                },
                "status": "accepted",
            },
            {
                "actor": {
                    "reference": f"Location/{a.local_id}",
                    "display": getattr(a.local, "nome", None),
                },
                "status": "accepted",
            },
        ],
        "comment": f"Modalidade: {a.modalidade}",
    }

    start_dt = getattr(a, "inicio", None)
    end_dt = _resolve_end_datetime(a)

    if start_dt is not None and end_dt is not None:
        resource["start"] = start_dt.isoformat()
        resource["end"] = end_dt.isoformat()
    elif start_dt is not None and status_fhir == "booked":
        # app-2/app-3: booked exige start + end.
        resource["start"] = start_dt.isoformat()
        resource["end"] = (
            start_dt + timedelta(minutes=DEFAULT_APPOINTMENT_DURATION_MINUTES)
        ).isoformat()

    return resource
