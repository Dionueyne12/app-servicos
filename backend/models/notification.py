from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class Notificacao(Base, TimestampMixin):
    __tablename__ = "notificacoes"

    id: Mapped[UUID] = uuid_pk_column()
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    solicitacao_id: Mapped[UUID | None] = mapped_column(ForeignKey("solicitacoes_servico.id"))
    tipo_notificacao: Mapped[str] = mapped_column(String(60), nullable=False)
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_leitura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    prioridade: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    canal: Mapped[str] = mapped_column(String(40), default="interna", nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario")
    solicitacao: Mapped["SolicitacaoServico | None"] = relationship("SolicitacaoServico")
