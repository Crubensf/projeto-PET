
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.modelos.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UsuarioCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Já existe usuário com este e-mail.")

    usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=get_password_hash(payload.senha),
        is_admin=payload.is_admin,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito de unicidade para o usuário.")
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # busca o usuário pelo email (que vem no campo username)
    usuario = db.scalar(select(Usuario).where(Usuario.email == form_data.username))

    # verifica senha
    if not usuario or not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")

    # cria token JWT
    token = create_access_token({"sub": str(usuario.id)})

    return TokenResponse(access_token=token)
