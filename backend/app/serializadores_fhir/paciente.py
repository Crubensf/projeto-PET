def paciente_para_fhir(p):
    identifiers = []

    # CPF (sempre presente)
    identifiers.append(
        {
            "use": "official",
            "system": "https://gov.br/cpf",
            "value": p.cpf,
        }
    )

    # CNS (opcional)
    if p.cartao_sus:
        identifiers.append(
            {
                "use": "official",
                "system": "https://saude.gov.br/sus/cartao",
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
        # Não publica extension com URL de exemplo (não resolvível em validadores).
    }
