from app.serializadores_fhir.utils import clean_fhir


def agendamento_para_fhir(a):
    if a is None:
        raise ValueError("Agendamento ausente para serialização FHIR.")

    agendamento_id = getattr(a, "id", None)
    if agendamento_id is None:
        raise ValueError("Agendamento sem id para serialização FHIR.")

    inicio = getattr(a, "inicio", None)
    if inicio is None:
        raise ValueError("Agendamento sem início para serialização FHIR.")

    if not hasattr(inicio, "isoformat"):
        raise ValueError("Valor de início inválido para serialização FHIR.")

    paciente_id = getattr(a, "paciente_id", None)
    profissional_id = getattr(a, "profissional_id", None)
    local_id = getattr(a, "local_id", None)
    if paciente_id is None or profissional_id is None or local_id is None:
        raise ValueError("Agendamento sem referências obrigatórias de participante.")

    # 🔥 Mapeamento PT → FHIR
    STATUS_MAP = {
        "agendado": "booked",
        "cancelado": "cancelled",
        "atendido": "fulfilled",
    }

    status_pt = (getattr(a, "status", None) or "agendado").lower()
    status_fhir = STATUS_MAP.get(status_pt, "booked")

    recurso = {
        "resourceType": "Appointment",
        "id": str(agendamento_id),
        "status": status_fhir,
        "start": inicio.isoformat(),
        "participant": [
            {
                "actor": {
                    "reference": f"Patient/{paciente_id}",
                },
                "status": "accepted",
            },
            {
                "actor": {
                    "reference": f"Practitioner/{profissional_id}",
                },
                "status": "accepted",
            },
            {
                "actor": {
                    "reference": f"Location/{local_id}",
                },
                "status": "accepted",
            },
        ],
    }

    especialidade_codigo = getattr(a.especialidade, "codigo", None)
    especialidade_nome = getattr(a.especialidade, "nome", None)
    if especialidade_codigo or especialidade_nome:
        coding = {}
        if especialidade_codigo:
            coding["code"] = especialidade_codigo
        if especialidade_nome:
            coding["display"] = especialidade_nome
        recurso["serviceType"] = [{"coding": [coding]}]

    nomes_participantes = (
        getattr(a.paciente, "nome", None),
        getattr(a.profissional, "nome", None),
        getattr(a.local, "nome", None),
    )
    for participant, nome in zip(recurso["participant"], nomes_participantes):
        if nome:
            participant["actor"]["display"] = nome

    modalidade = getattr(a, "modalidade", None)
    if modalidade:
        recurso["comment"] = f"Modalidade: {modalidade}"

    return clean_fhir(recurso)
