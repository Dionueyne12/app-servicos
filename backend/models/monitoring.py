from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, CreatedAtMixin, uuid_pk_column


class MonitoramentoSistema(Base, CreatedAtMixin):
    __tablename__ = "monitoramento_sistema"

    id: Mapped[UUID] = uuid_pk_column()
    tipo_alerta: Mapped[str] = mapped_column(String(80), nullable=False)
    nivel_alerta: Mapped[str] = mapped_column(String(20), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    origem: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="ativo", nullable=False)
