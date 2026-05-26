from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class PagamentoSimulado(Base, TimestampMixin):
    __tablename__ = "pagamentos_simulados"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("solicitacoes_servico.id"),
        unique=True,
        nullable=False,
    )
    valor_mao_obra: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_material: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_comissao: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_prestador: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_empresa: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status_pagamento: Mapped[str] = mapped_column(String(40), default="simulado", nullable=False)

    solicitacao: Mapped["SolicitacaoServico"] = relationship(
        "SolicitacaoServico",
        back_populates="pagamento",
    )
    repasses: Mapped[list["Repasse"]] = relationship("Repasse", back_populates="pagamento")


class Repasse(Base, TimestampMixin):
    __tablename__ = "repasses"

    id: Mapped[UUID] = uuid_pk_column()
    pagamento_id: Mapped[UUID] = mapped_column(ForeignKey("pagamentos_simulados.id"), nullable=False)
    destinatario_usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    empresa_fornecedora_id: Mapped[UUID | None] = mapped_column(ForeignKey("empresas_fornecedoras.id"))
    tipo_repasse: Mapped[str] = mapped_column(String(40), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status_repasse: Mapped[str] = mapped_column(String(40), default="pendente", nullable=False)

    pagamento: Mapped[PagamentoSimulado] = relationship("PagamentoSimulado", back_populates="repasses")


class Pagamento(Base, TimestampMixin):
    __tablename__ = "pagamentos"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("solicitacoes_servico.id"),
        unique=True,
        nullable=False,
    )
    cliente_id: Mapped[UUID] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    prestador_id: Mapped[UUID] = mapped_column(ForeignKey("prestadores.id"), nullable=False)
    valor_mao_obra: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_material: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_comissao_plataforma: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_prestador: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    valor_fornecedor: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status_pagamento: Mapped[str] = mapped_column(String(40), default="aguardando_pagamento", nullable=False)
    metodo_pagamento: Mapped[str] = mapped_column(String(40), nullable=False)
    data_pagamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_liberacao_repasse: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    comprovante_pagamento: Mapped[str | None] = mapped_column(Text)

    solicitacao: Mapped["SolicitacaoServico"] = relationship("SolicitacaoServico")
    cliente: Mapped["Cliente"] = relationship("Cliente")
    prestador: Mapped["Prestador"] = relationship("Prestador")
    movimentacoes: Mapped[list["MovimentacaoCarteira"]] = relationship(
        "MovimentacaoCarteira",
        back_populates="pagamento",
    )


class CarteiraUsuario(Base, TimestampMixin):
    __tablename__ = "carteira_usuario"

    id: Mapped[UUID] = uuid_pk_column()
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    saldo_disponivel: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    saldo_pendente: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    saldo_bloqueado: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_recebido: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_movimentado: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario")
    movimentacoes: Mapped[list["MovimentacaoCarteira"]] = relationship(
        "MovimentacaoCarteira",
        back_populates="carteira",
    )


class MovimentacaoCarteira(Base, TimestampMixin):
    __tablename__ = "movimentacoes_carteira"

    id: Mapped[UUID] = uuid_pk_column()
    carteira_id: Mapped[UUID] = mapped_column(ForeignKey("carteira_usuario.id"), nullable=False)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    pagamento_id: Mapped[UUID | None] = mapped_column(ForeignKey("pagamentos.id"))
    tipo_movimentacao: Mapped[str] = mapped_column(String(40), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    saldo_disponivel_apos: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    saldo_pendente_apos: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    saldo_bloqueado_apos: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    carteira: Mapped[CarteiraUsuario] = relationship("CarteiraUsuario", back_populates="movimentacoes")
    pagamento: Mapped[Pagamento | None] = relationship("Pagamento", back_populates="movimentacoes")
