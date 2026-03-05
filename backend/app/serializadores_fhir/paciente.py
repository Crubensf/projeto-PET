from app.serializadores_fhir.utils import clean_fhir


MOTHER_NAME_EXT_URL = "https://example.org/fhir/StructureDefinition/patient-mothersName"


def paciente_para_fhir(p):
    if p is None:
        raise ValueError("Paciente ausente para serialização FHIR.")

    paciente_id = getattr(p, "id", None)
    if paciente_id is None:
        raise ValueError("Paciente sem id para serialização FHIR.")

    data_nascimento = getattr(p, "data_nascimento", None)
    if data_nascimento is None:
        raise ValueError("Paciente sem data_nascimento para serialização FHIR.")

    if not hasattr(data_nascimento, "isoformat"):
        raise ValueError("data_nascimento inválida para serialização FHIR.")

    nome = getattr(p, "nome", None)
    if not nome:
        raise ValueError("Paciente sem nome para serialização FHIR.")

    identifiers = []
    cpf = getattr(p, "cpf", None)
    cartao_sus = getattr(p, "cartao_sus", None)

    # CPF
    if cpf:
        identifiers.append(
            {
                "use": "official",
                "system": "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cpf",
                "value": cpf,
            }
        )

    # CNS (opcional)
    if cartao_sus:
        identifiers.append(
            {
                "use": "official",
                "system": "http://rnds.saude.gov.br/fhir/r4/NamingSystem/cns",
                "value": cartao_sus,
            }
        )

    resource = {
        "resourceType": "Patient",
        "id": str(paciente_id),
        "identifier": identifiers,
        "name": [
            {
                "use": "official",
                "text": nome,
            }
        ],
        "birthDate": data_nascimento.isoformat(),
    }

    telefone = getattr(p, "telefone", None)
    if telefone:
        resource["telecom"] = [
            {
                "system": "phone",
                "value": telefone,
                "use": "mobile",
            }
        ]

    endereco = getattr(p, "endereco", None)
    municipio = getattr(p, "municipio", None)
    if endereco or municipio:
        resource["address"] = [
            {
                "text": endereco,
                "city": municipio,
                "country": "BR",
            }
        ]

    nome_mae = getattr(p, "nome_mae", None)
    if nome_mae:
        resource["extension"] = [
            {
                "url": MOTHER_NAME_EXT_URL,
                "valueString": nome_mae,
            }
        ]

    return clean_fhir(resource)
