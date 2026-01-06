def local_para_fhir(l):
    return {
        "resourceType": "Location",
        "id": str(l.id),
        "name": l.nome,
        "address": {
            "line": [l.endereco] if l.endereco else [],
            "city": l.municipio,
            "country": "BR",
        },
    }
