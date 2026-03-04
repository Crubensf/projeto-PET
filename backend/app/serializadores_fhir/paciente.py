MOTHER_NAME_EXT_URL = "https://example.org/fhir/StructureDefinition/patient-mothersName"


def paciente_para_fhir(p):
    identifiers = []

    # CPF (sempre presente)
    identifiers.append(
        {
            "use": "official",
            "system": "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cpf",
            "value": p.cpf,
        }
    )

    # CNS (opcional)
    if p.cartao_sus:
        identifiers.append(
            {
                "use": "official",
                "system": "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cns",
                "value": p.cartao_sus,
            }
        )

    return {
        "resourceType": "Patient",
        "id": str(p.id),
        "identifier": identifiers,
        "name": [
            {
                "use": "official",
                "text": p.nome,
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": p.telefone,
                "use": "mobile",
            }
        ],
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
