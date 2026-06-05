from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from app.extensions import db
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cargo import Cargo
    from .chave_publica import ChavePublica
    from .documento import Documento
    from .assinante_documento import AssinanteDocumento


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    oab: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)

    senha: Mapped[str] = mapped_column(String(255), nullable=False)

    id_cargo: Mapped[int] = mapped_column(
        ForeignKey("cargos.id"),
        nullable=False
    )

    cargo: Mapped["Cargo"] = relationship("Cargo", back_populates="usuarios")

    chaves_publicas: Mapped[list["ChavePublica"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    convites_assinaturas: Mapped[list["AssinanteDocumento"]] = relationship(
        back_populates="usuario"
    )

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"
