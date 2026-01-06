def profissional_para_fhir(prof):
    return {
        "resourceType": "Practitioner",
        "id": str(prof.id),
        "name": [{"text": prof.nome}],
    }
