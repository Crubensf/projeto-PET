from app.serializadores_fhir.utils import clean_fhir


def profissional_para_fhir(prof):
    if prof is None:
        raise ValueError("Profissional ausente para serialização FHIR.")

    prof_id = getattr(prof, "id", None)
    if prof_id is None:
        raise ValueError("Profissional sem id para serialização FHIR.")

    nome = getattr(prof, "nome", None)
    if not nome:
        raise ValueError("Profissional sem nome para serialização FHIR.")

    resource = {
        "resourceType": "Practitioner",
        "id": str(prof_id),
        "name": [{"text": nome}],
    }

    return clean_fhir(resource)
