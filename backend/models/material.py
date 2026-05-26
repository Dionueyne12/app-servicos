from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class MaterialServico(Base, TimestampMixin):
    __tablename__ = "materiais_servico"

    id: Mapped[UUID] = uuid_pk_column()
    solicitacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("solicitacoes_servico.id"),
        unique=True,
        nullable=False,
    )
    prestador_id: Mapped[UUID | None] = mapped_column(ForeignKey("prestadores.id"))
    escolha_cliente: Mapped[str] = mapped_column(String(40), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    descricao_material: Mapped[str | None] = mapped_column(Text)
    marca_modelo: Mapped[str | None] = mapped_column(String(160))
    foto_url: Mapped[str | None] = mapped_column(Text)
    valor_estimado: Mapped[float | None] = mapped_column(Numeric(10, 2))
    limite_valor_cliente: Mapped[float | None] = mapped_column(Numeric(10, 2))
    empresa_fornecedora_id: Mapped[UUID | None] = mapped_column(ForeignKey("empresas_fornecedoras.id"))
    necessita_aprovacao_cliente: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aprovado_cliente: Mapped[bool | None] = mapped_column(Boolean)
    aprovado_pelo_cliente: Mapped[bool | None] = mapped_column(Boolean)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_aprovacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observacao_cliente: Mapped[str | None] = mapped_column(Text)
    status_material: Mapped[str] = mapped_column(
        String(40),
        default="pendente_avaliacao",
        nullable=False,
    )

    solicitacao: Mapped["SolicitacaoServico"] = relationship(
        "SolicitacaoServico",
        back_populates="material",
    )
    empresa_fornecedora: Mapped["EmpresaFornecedora | None"] = relationship(
        "EmpresaFornecedora",
        back_populates="materiais",
    )
