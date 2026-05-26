from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAtMixin, uuid_pk_column


class HistoricoStatus(Base, CreatedAtMixin):
    __tablename__ = "historico_status"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(ForeignKey("solicitacoes_servico.id"), nullable=False)
    status_anterior: Mapped[str | None] = mapped_column(ForeignKey("status_servico.codigo"))
    status_novo: Mapped[str] = mapped_column(ForeignKey("status_servico.codigo"), nullable=False)
    alterado_por_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)

    solicitacao: Mapped["SolicitacaoServico"] = relationship("SolicitacaoServico")
    alterado_por: Mapped["Usuario"] = relationship("Usuario")


class HistoricoEdicao(Base, CreatedAtMixin):
    __tablename__ = "historico_edicoes"

    id: Mapped[UUID] = uuid_pk_column()
    entidade: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    campo: Mapped[str] = mapped_column(String(120), nullable=False)
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_novo: Mapped[str | None] = mapped_column(Text)
    alterado_por_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    origem: Mapped[str] = mapped_column(String(40), default="backend", nullable=False)

    alterado_por: Mapped["Usuario"] = relationship("Usuario")
