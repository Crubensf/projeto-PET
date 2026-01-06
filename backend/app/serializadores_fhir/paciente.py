def paciente_para_fhir(p):
    return {
        "resourceType": "Patient",
        "id": str(p.id),
        "identifier": ([] if not p.cns else [{
            "use": "official",
            "type": {"text": "CNS"},
            "system": "http://example.org/fhir/NamingSystem/cns",
            "value": p.cns
        }]),
        "name": [{"use": "official", "text": p.nome}],
        "telecom": [{"system": "phone", "value": p.telefone, "use": "mobile"}],
        "birthDate": p.data_nascimento.isoformat(),
        "address": [{
            "use": "home",
            "line": [p.endereco] if p.endereco else [],
            "city": p.municipio,
            "country": "BR"
        }],
        "contact": [{
            "relationship": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                    "code": "MTH",
                    "display": "Mother"
                }],
                "text": "Mãe"
            }],
            "name": {"text": p.nome_mae}
        }]
    }
