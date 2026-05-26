from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAtMixin, TimestampMixin, uuid_pk_column


class CategoriaServico(Base, TimestampMixin):
    __tablename__ = "categorias_servico"

    id: Mapped[UUID] = uuid_pk_column()
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    servicos: Mapped[list["ServicoTabelado"]] = relationship(
        "ServicoTabelado",
        back_populates="categoria",
    )


class ServicoTabelado(Base, TimestampMixin):
    __tablename__ = "servicos_tabelados"

    id: Mapped[UUID] = uuid_pk_column()
    categoria_id: Mapped[UUID] = mapped_column(ForeignKey("categorias_servico.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    preco_mao_obra: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tempo_estimado_minutos: Mapped[int] = mapped_column(nullable=False)
    precisa_material: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria: Mapped[CategoriaServico] = relationship("CategoriaServico", back_populates="servicos")
    solicitacoes: Mapped[list["SolicitacaoServico"]] = relationship(
        "SolicitacaoServico",
        back_populates="servico_tabelado",
    )


class StatusServico(Base, CreatedAtMixin):
    __tablename__ = "status_servico"

    codigo: Mapped[str] = mapped_column(String(60), primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    ordem: Mapped[int] = mapped_column(nullable=False)
    finaliza_fluxo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
