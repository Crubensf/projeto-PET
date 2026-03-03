def agendamento_para_fhir(a):
    # 🔥 Mapeamento PT → FHIR
    STATUS_MAP = {
        "agendado": "booked",
        "cancelado": "cancelled",
        "atendido": "fulfilled",
    }

    status_pt = (a.status or "agendado").lower()
    status_fhir = STATUS_MAP.get(status_pt, "booked")

    return {
        "resourceType": "Appointment",
        "id": str(a.id),
        "status": status_fhir,
        "start": a.inicio.isoformat(),
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