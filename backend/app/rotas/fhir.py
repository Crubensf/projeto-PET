from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modelos.paciente import Paciente
from app.modelos.agendamento import Agendamento

router = APIRouter(prefix="/fhir", tags=["FHIR R4"])


MOTHER_NAME_EXT_URL = "https://example.org/fhir/StructureDefinition/patient-mothersName"


def patient_to_fhir(p: Paciente) -> dict:
    return {
        "resourceType": "Patient",
        "id": str(p.id),
        "identifier": [
            {
                "system": "https://saude.gov.br/sus/cartao",
                "value": p.cartao_sus,
            }
        ],
        "name": [
            {
                "use": "official",
                "text": p.nome,
            }
        ],
        "telecom": [
            {"system": "phone", "value": p.telefone, "use": "mobile"}
        ],
        "birthDate": p.data_nascimento.isoformat(),
        "address": [
            {
                "text": p.endereco,
                "city": p.municipio,
            }
        ],
        "extension": [
            {
                "url": MOTHER_NAME_EXT_URL,
                "valueString": p.nome_mae,
            }
        ],
    }


def appointment_to_fhir(a: Agendamento) -> dict:
    return {
        "resourceType": "Appointment",
        "id": str(a.id),
        "status": a.status,
        "start": a.inicio.isoformat(),
        "serviceType": [
            {
                "coding": [
                    {"code": getattr(a.especialidade, "codigo", None), "display": getattr(a.especialidade, "nome", None)}
                ]
            }
        ],
        "participant": [
            {
                "actor": {"reference": f"Patient/{a.paciente_id}", "display": getattr(a.paciente, "nome", None)},
                "status": "accepted",
            },
            {
                "actor": {"reference": f"Practitioner/{a.profissional_id}", "display": getattr(a.profissional, "nome", None)},
                "status": "accepted",
            },
            {
                "actor": {"reference": f"Location/{a.local_id}", "display": getattr(a.local, "nome", None)},
                "status": "accepted",
            },
        ],
        "comment": f"Modalidade: {a.modalidade}",
    }


@router.get("/patient/{paciente_id}")
def get_patient_fhir(paciente_id: int, db: Session = Depends(get_db)):
    p = db.get(Paciente, paciente_id)
    if not p:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return patient_to_fhir(p)


@router.get("/appointment/{agendamento_id}")
def get_appointment_fhir(agendamento_id: int, db: Session = Depends(get_db)):
    a = db.get(Agendamento, agendamento_id)
    if not a:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    # garante relacionamentos carregados (a depender da config)
    _ = a.paciente, a.profissional, a.especialidade, a.local
    return appointment_to_fhir(a)
