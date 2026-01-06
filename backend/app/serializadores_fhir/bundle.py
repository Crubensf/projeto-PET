from app.serializadores_fhir.paciente import paciente_para_fhir
from app.serializadores_fhir.profissional import profissional_para_fhir
from app.serializadores_fhir.local import local_para_fhir
from app.serializadores_fhir.agendamento import agendamento_para_fhir


def bundle_comprovante(paciente, profissional, local, agendamento):
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": paciente_para_fhir(paciente)},
            {"resource": profissional_para_fhir(profissional)},
            {"resource": local_para_fhir(local)},
            {"resource": agendamento_para_fhir(agendamento)},
        ],
    }
