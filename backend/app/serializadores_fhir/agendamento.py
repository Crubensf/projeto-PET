def agendamento_para_fhir(a):
    # status no seu banco já está como "booked"/"cancelled" etc.
    status = (a.status or "booked").lower()

    return {
        "resourceType": "Appointment",
        "id": str(a.id),
        "status": status,
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
                "actor": {"reference": f"Patient/{a.paciente_id}", "display": getattr(a.paciente, "nome", None)},
                "status": "accepted",
            },
            {
                "actor": {"reference": f"Practitioner/{a.profissional_id}", "display": getattr(a.profissional, "nome", None)},
                "status": "accepted",
            },
            {
                "actor": {"reference": f"Location/{a.local_id}", "display": getattr(a.local, "nome", None)},
                "status": "accepted",
            },
        ],
        "comment": f"Modalidade: {a.modalidade}",
    }
