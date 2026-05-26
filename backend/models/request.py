from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAtMixin, TimestampMixin, uuid_pk_column


class SolicitacaoServico(Base, TimestampMixin):
    __tablename__ = "solicitacoes_servico"

    id: Mapped[UUID] = uuid_pk_column()
    cliente_id: Mapped[UUID] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    prestador_id: Mapped[UUID | None] = mapped_column(ForeignKey("prestadores.id"))
    servico_tabelado_id: Mapped[UUID | None] = mapped_column(ForeignKey("servicos_tabelados.id"))
    categoria_id: Mapped[UUID | None] = mapped_column(ForeignKey("categorias_servico.id"))
    tipo_servico: Mapped[str] = mapped_column(String(30), default="tabelado", nullable=False)
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    cidade: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str | None] = mapped_column(String(2))
    urgencia: Mapped[str] = mapped_column(String(30), default="normal", nullable=False)
    melhor_horario: Mapped[str | None] = mapped_column(String(120))
    observacoes: Mapped[str | None] = mapped_column(Text)
    status_codigo: Mapped[str] = mapped_column(ForeignKey("status_servico.codigo"), nullable=False)
    preco_mao_obra_snapshot: Mapped[float | None] = mapped_column(Numeric(10, 2))
    tempo_estimado_snapshot_minutos: Mapped[int | None]
    aceito_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    iniciado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_conclusao_prestador: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_confirmacao_cliente: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observacao_problema: Mapped[str | None] = mapped_column(Text)

    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="solicitacoes")
    prestador: Mapped["Prestador | None"] = relationship("Prestador", back_populates="solicitacoes")
    servico_tabelado: Mapped["ServicoTabelado | None"] = relationship(
        "ServicoTabelado",
        back_populates="solicitacoes",
    )
    status: Mapped["StatusServico"] = relationship("StatusServico")
    categoria: Mapped["CategoriaServico | None"] = relationship("CategoriaServico")
    fotos: Mapped[list["FotoServico"]] = relationship("FotoServico", back_populates="solicitacao")
    mensagens: Mapped[list["MensagemSolicitacao"]] = relationship(
        "MensagemSolicitacao",
        back_populates="solicitacao",
    )
    material: Mapped["MaterialServico | None"] = relationship(
        "MaterialServico",
        back_populates="solicitacao",
    )
    pagamento: Mapped["PagamentoSimulado | None"] = relationship(
        "PagamentoSimulado",
        back_populates="solicitacao",
    )


class FotoServico(Base, TimestampMixin):
    __tablename__ = "fotos_servico"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(ForeignKey("solicitacoes_servico.id"), nullable=False)
    enviado_por_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(Text, nullable=False)
    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(nullable=False)
    tipo_foto: Mapped[str] = mapped_column(String(40), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)

    solicitacao: Mapped[SolicitacaoServico] = relationship(
        "SolicitacaoServico",
        back_populates="fotos",
    )


class MensagemSolicitacao(Base, TimestampMixin):
    __tablename__ = "mensagens_solicitacao"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(ForeignKey("solicitacoes_servico.id"), nullable=False)
    remetente_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    destinatario_usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tipo_mensagem: Mapped[str] = mapped_column(String(40), default="texto", nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    arquivo_url: Mapped[str | None] = mapped_column(Text)
    visualizada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_visualizacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    solicitacao: Mapped[SolicitacaoServico] = relationship(
        "SolicitacaoServico",
        back_populates="mensagens",
    )
    remetente: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=[remetente_usuario_id],
    )
    destinatario: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=[destinatario_usuario_id],
    )
