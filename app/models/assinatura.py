from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chave_publica import ChavePublica
    from .documento import Documento
    from .assinante_documento import AssinanteDocumento


class Assinatura(db.Model):
    __tablename__ = 'assinaturas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    documento_id: Mapped[int] = mapped_column(
        ForeignKey('documentos.id'),
        index=True
    )

    assinante_id: Mapped[int] = mapped_column(
        ForeignKey('assinantes_documentos.id'),
        index=True,
        nullable=False
    )

    hash_assinatura: Mapped[str] = mapped_column(String(64), nullable=False)

    assinatura_digital: Mapped[str] = mapped_column(Text, nullable=False)

    assinado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    algoritmo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='ECC/ECDSA-P256'
    )

    chave_publica_id: Mapped[int] = mapped_column(
        ForeignKey('chaves_publicas.id'),
        index=True,
        nullable=False
    )

    documento: Mapped['Documento'] = relationship(
        back_populates='assinaturas'
    )

    chave_publica: Mapped['ChavePublica'] = relationship(
        back_populates='assinaturas'
    )

    assinante: Mapped['AssinanteDocumento'] = relationship(
        back_populates='assinatura',
        uselist=False
    )

    def __repr__(self):
        return (
            f"<Assinatura id={self.id} documento_id={self.documento_id}"
            f"chave_publica_id={self.chave_publica_id}"
            f"assinado_em='{self.assinado_em}'>"
        )
