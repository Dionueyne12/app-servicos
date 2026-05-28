from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class GarantiaServico(Base, TimestampMixin):
    __tablename__ = "garantias_servico"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(ForeignKey("solicitacoes_servico.id"), unique=True, nullable=False)
    prestador_id: Mapped[UUID] = mapped_column(ForeignKey("prestadores.id"), nullable=False)
    cliente_id: Mapped[UUID] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    servico_tabelado_id: Mapped[UUID | None] = mapped_column(ForeignKey("servicos_tabelados.id"))
    pagamento_simulado_id: Mapped[UUID | None] = mapped_column(ForeignKey("pagamentos_simulados.id"))
    pagamento_id: Mapped[UUID | None] = mapped_column(ForeignKey("pagamentos.id"))
    data_inicio_garantia: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_fim_garantia: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_garantia: Mapped[str] = mapped_column(String(40), default="ativa", nullable=False)
    valor_retido: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_liberado_inicial: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    percentual_retencao: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    dias_garantia: Mapped[int] = mapped_column(default=0, nullable=False)
    dias_liberacao_primeiro_repasse: Mapped[int] = mapped_column(default=0, nullable=False)
    descricao_problema: Mapped[str | None] = mapped_column(Text)
    observacao_cliente: Mapped[str | None] = mapped_column(Text)
    observacao_admin: Mapped[str | None] = mapped_column(Text)
    fotos: Mapped[str | None] = mapped_column(Text)
    bloqueio_repasse: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    procedente: Mapped[bool | None] = mapped_column(Boolean)
    data_acionamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_resolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    solicitacao: Mapped["SolicitacaoServico"] = relationship("SolicitacaoServico", back_populates="garantia")
    prestador: Mapped["Prestador"] = relationship("Prestador")
    cliente: Mapped["Cliente"] = relationship("Cliente")
    servico_tabelado: Mapped["ServicoTabelado | None"] = relationship("ServicoTabelado")
