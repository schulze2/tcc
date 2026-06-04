from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.extensions import db

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Cargo(db.Model):
    __tablename__ = "cargos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    cargo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="cargo",
    )

    def __repr__(self):
        return f"<Cargo {self.cargo}>"
