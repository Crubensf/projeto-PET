from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Profissional(Base):
    __tablename__ = "profissionais"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)

    especialidade_id: Mapped[int] = mapped_column(ForeignKey("especialidades.id"))
    especialidade = relationship("Especialidade")
