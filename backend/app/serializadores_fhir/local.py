from app.serializadores_fhir.utils import clean_fhir


def local_para_fhir(l):
    if l is None:
        raise ValueError("Local de atendimento ausente para serialização FHIR.")

    local_id = getattr(l, "id", None)
    if local_id is None:
        raise ValueError("Local de atendimento sem id para serialização FHIR.")

    nome = getattr(l, "nome", None)
    if not nome:
        raise ValueError("Local de atendimento sem nome para serialização FHIR.")

    endereco = getattr(l, "endereco", None)
    municipio = getattr(l, "municipio", None)

    resource = {
        "resourceType": "Location",
        "id": str(local_id),
        "name": nome,
        "address": {
            "line": [endereco] if endereco else [],
            "city": municipio,
            "country": "BR",
        },
    }

    return clean_fhir(resource)
