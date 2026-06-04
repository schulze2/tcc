from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .usuario import Usuario
    from .documento import Documento
    from .assinatura import Assinatura


class AssinanteDocumento(db.Model):
    __tablename__ = "assinantes_documentos"
    __table_args__ = (
        UniqueConstraint(
            "documento_id",
            "email",
            name="uq_assiantes_documento_documento_email"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    documento_id: Mapped[int] = mapped_column(
        ForeignKey('documentos.id'),
        nullable=False,
    )

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey('usuarios.id'),
        nullable=True,
    )

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='pendente'
    )

    token_convite: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    convidado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    assinado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    recusado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    motivo_recusa: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    documento: Mapped['Documento'] = relationship(
        back_populates='assinantes'
    )

    usuario: Mapped['Usuario'] = relationship(
        back_populates='convites_assinaturas',
    )

    assinatura: Mapped['Assinatura'] = relationship(
        back_populates="assinante",
        uselist=False,
        cascade="all, delete-orphan"
    )
