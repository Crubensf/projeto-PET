def agendamento_para_fhir(a):
    return {
        "resourceType": "Appointment",
        "id": str(a.id),
        "status": (a.status or "BOOKED").lower(),
        "description": f"{a.modalidade}",
        "start": a.inicio.isoformat(),
        "end": a.fim.isoformat(),
        "participant": [
            {"actor": {"reference": f"Patient/{a.paciente_id}"}, "status": "accepted"},
            {
                "actor": {"reference": f"Practitioner/{a.solicitante_profissional_id}"},
                "type": [{"text": "Profissional solicitante (quem fez)"}],
                "status": "accepted"
            },
            {
                "actor": {"reference": f"Practitioner/{a.profissional_id}"},
                "type": [{"text": "Profissional executante (quem atenderá)"}],
                "status": "accepted"
            },
            {"actor": {"reference": f"Location/{a.local_id}"}, "status": "accepted"}
        ]
    }
