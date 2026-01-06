from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.environment import settings
from app.core.database import Base, engine

# Importa modelos para garantir criação das tabelas
from app import modelos  # noqa: F401

from app.rotas.pacientes import router as pacientes_router
from app.rotas.profissionais import router as profissionais_router
from app.rotas.especialidades import router as especialidades_router
from app.rotas.locais import router as locais_router
from app.rotas.agendamentos import router as agendamentos_router
from app.rotas.slots import router as slots_router
from app.rotas.dashboard import router as dashboard_router
from app.rotas.fhir import router as fhir_router

app = FastAPI(title=settings.API_TITLE)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(especialidades_router)
app.include_router(profissionais_router)
app.include_router(locais_router)
app.include_router(pacientes_router)
app.include_router(agendamentos_router)
app.include_router(slots_router)
app.include_router(dashboard_router)
app.include_router(fhir_router)


@app.get("/")
def healthcheck():
    return {"status": "ok", "docs": "/docs", "fhir": "/fhir", "dashboard": "/dashboard"}
