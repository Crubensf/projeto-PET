from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    nome: Mapped[str] = mapped_column(String(140), index=True)
    cartao_sus: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    data_nascimento: Mapped["Date"] = mapped_column(Date)
    telefone: Mapped[str] = mapped_column(String(30))

    municipio: Mapped[str] = mapped_column(String(120))
    endereco: Mapped[str] = mapped_column(String(200))

    nome_mae: Mapped[str] = mapped_column(String(140))
