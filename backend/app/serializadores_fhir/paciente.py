MOTHER_NAME_EXT_URL = "https://example.org/fhir/StructureDefinition/patient-mothersName"


def paciente_para_fhir(p):
    return {
        "resourceType": "Patient",
        "id": str(p.id),
        "identifier": [
            {
                "use": "official",
                "system": "https://saude.gov.br/sus/cartao",
                "value": p.cartao_sus,
            }
        ],
        "name": [{"use": "official", "text": p.nome}],
        "telecom": [{"system": "phone", "value": p.telefone, "use": "mobile"}],
        "birthDate": p.data_nascimento.isoformat(),
        "address": [
            {
                "text": p.endereco,
                "city": p.municipio,
                "country": "BR",
            }
        ],
        "extension": [
            {
                "url": MOTHER_NAME_EXT_URL,
                "valueString": p.nome_mae,
            }
        ],
    }
