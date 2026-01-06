def profissional_para_fhir(prof):
    out = {
        "resourceType": "Practitioner",
        "id": str(prof.id),
        "name": [{"text": prof.nome}],
    }
    if prof.registro_conselho:
        out["identifier"] = [{
            "system": "http://example.org/fhir/NamingSystem/registro-conselho",
            "value": prof.registro_conselho
        }]
    return out
