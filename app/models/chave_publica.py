
from sqlalchemy import Text, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING, List

from app.extensions import db

if TYPE_CHECKING:
    from .usuario import Usuario
    from .assinatura import Assinatura


class ChavePublica(db.Model):
    __tablename__ = 'chaves_publicas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id'),
        nullable=False,
        index=True
    )

    usuario: Mapped['Usuario'] = relationship(
        'Usuario', back_populates='chaves_publicas')

    chave_publica: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='ativa')

    assinaturas: Mapped[List['Assinatura']] = relationship(
        back_populates='chave_publica'
    )

    def __repr__(self):
        return f"<ChavePublica id={self.id} id_usuario={self.id_usuario} status='{self.status}'>"
