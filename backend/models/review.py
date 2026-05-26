from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class Avaliacao(Base, TimestampMixin):
    __tablename__ = "avaliacoes"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(ForeignKey("solicitacoes_servico.id"), nullable=False)
    avaliador_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    avaliado_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo_avaliacao: Mapped[str] = mapped_column(String(40), nullable=False)
    nota: Mapped[int] = mapped_column(nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)

    solicitacao: Mapped["SolicitacaoServico"] = relationship("SolicitacaoServico")
    avaliador: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[avaliador_usuario_id])
    avaliado: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[avaliado_usuario_id])
