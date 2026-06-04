from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .documento import Documento


class RegistroBlockchain(db.Model):
    __tablename__ = "registros_blockchain"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    documento_id: Mapped[int] = mapped_column(
        ForeignKey('documentos.id'),
        nullable=False,
        index=True
    )

    documento_ref: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    hash_registrado: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True
    )

    tx_hash: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    endereco_contrato: Mapped[str] = mapped_column(
        String(42),
        nullable=False
    )

    endereco_carteira: Mapped[str] = mapped_column(
        String(42),
        nullable=False
    )

    numero_bloco: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rede: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Sepolia/testnet'
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default='pendente'
    )

    registrado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    documento: Mapped['Documento'] = relationship(
        back_populates='registros_blockchain'
    )
