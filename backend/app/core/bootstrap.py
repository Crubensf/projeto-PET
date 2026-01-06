from app.core.database import SessionLocal
from app.modelos.especialidade import Especialidade
from app.modelos.local_atendimento import LocalAtendimento
from app.modelos.profissional import Profissional

ESPECIALIDADES = [
    ("Clínico Geral", True),
    ("Ginecologia e Obstetrícia", False),
    ("Hepatologia", False),
    ("Pediatria", False),
    ("Cardiologia", False),
    ("Dermatologia", False),
    ("Neurologia", False),
    ("Psiquiatria", False),
    ("Endocrinologia", False),
    ("Ortopedia", False),
    ("Otorrinolaringologia", False),
    ("Urologia", False),
    ("Psicologia", True),
    ("Nutrição", True),
    ("Endoscopia digestiva alta", False),
    ("Ultrassonografia", False),
]

LOCAIS = [
    ("UBS Centro", "Av. Principal, 1000", "Teresina", "PI"),
    ("UBS Vila Esperança", "Rua X, 123", "Teresina", "PI"),
]

PROFISSIONAIS = [
    ("Dra. Ana Paula", "CRM-PI 12345", "Clínico Geral"),
    ("Dr. João Silva", "CRM-PI 54321", "Cardiologia"),
    ("Dra. Maria Souza", "CRM-PI 77777", "Ginecologia e Obstetrícia"),
    ("Psicóloga Carla Lima", "CRP-PI 9999", "Psicologia"),
    ("Nutricionista Bruno", "CRN-PI 8888", "Nutrição"),
]

def bootstrap_all():
    db = SessionLocal()
    try:
        # Especialidades
        for nome, tele in ESPECIALIDADES:
            existe = db.query(Especialidade).filter_by(nome=nome).first()
            if not existe:
                db.add(Especialidade(nome=nome, permite_telemedicina=tele))
        db.commit()

        # Locais
        for nome, endereco, municipio, estado in LOCAIS:
            existe = db.query(LocalAtendimento).filter_by(nome=nome).first()
            if not existe:
                db.add(LocalAtendimento(nome=nome, endereco=endereco, municipio=municipio, estado=estado))
        db.commit()

        # Profissionais
        for nome, registro, esp_nome in PROFISSIONAIS:
            esp = db.query(Especialidade).filter_by(nome=esp_nome).first()
            if not esp:
                continue
            existe = db.query(Profissional).filter_by(nome=nome).first()
            if not existe:
                db.add(Profissional(nome=nome, registro_conselho=registro, especialidade_id=esp.id))
        db.commit()
    finally:
        db.close()
