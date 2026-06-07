

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .usuario import Usuario
    from .assinatura import Assinatura
    from .assinante_documento import AssinanteDocumento
    from .registro_blockchain import RegistroBlockchain


class Documento(db.Model):
    __tablename__ = 'documentos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    nome_arquivo_original: Mapped[str] = mapped_column(
        String(255), nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    hash_original: Mapped[str] = mapped_column(String(64), nullable=False)

    nome_arquivo_assinado: Mapped[str] = mapped_column(
        String(255), nullable=True)
    caminho_arquivo_assinado: Mapped[str] = mapped_column(
        String(255), nullable=True)
    hash_arquivo_assinado: Mapped[str] = mapped_column(
        String(64), nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='aguardando_assinatura')

    criado_em: Mapped[DateTime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id'),
        nullable=False
    )

    usuario: Mapped['Usuario'] = relationship(
        'Usuario', back_populates='documentos')

    prioridade: Mapped[str] = mapped_column(
        String(20), nullable=False, default="normal")

    cancelado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True)

    motivo_cancelamento: Mapped[str | None] = mapped_column(
        String(255), nullable=True)

    assinaturas: Mapped[List['Assinatura']] = relationship(
        back_populates='documento', cascade='all, delete-orphan'
    )

    registros_blockchain: Mapped[List['RegistroBlockchain']] = relationship(
        back_populates='documento', cascade='all, delete-orphan'
    )

    assinantes: Mapped[List['AssinanteDocumento']] = relationship(
        back_populates='documento', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Documento id={self.id} nome_arquivo_original='{self.nome_arquivo_original}' status='{self.status}'>"
