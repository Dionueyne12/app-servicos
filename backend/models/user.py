from uuid import UUID

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, uuid_pk_column


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[UUID] = uuid_pk_column()
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_usuario: Mapped[str] = mapped_column(String(30), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    cliente: Mapped["Cliente | None"] = relationship("Cliente", back_populates="usuario")
    prestador: Mapped["Prestador | None"] = relationship("Prestador", back_populates="usuario")
    empresa_fornecedora: Mapped["EmpresaFornecedora | None"] = relationship(
        "EmpresaFornecedora",
        back_populates="usuario",
    )


class Cliente(Base, TimestampMixin):
    __tablename__ = "clientes"

    id: Mapped[UUID] = uuid_pk_column()
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    documento: Mapped[str | None] = mapped_column(String(20))
    endereco_principal: Mapped[str | None] = mapped_column(Text)
    bairro: Mapped[str | None] = mapped_column(String(120))
    cidade: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str | None] = mapped_column(String(2))
    media_notas: Mapped[float] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    total_avaliacoes: Mapped[int] = mapped_column(default=0, nullable=False)
    total_servicos_solicitados: Mapped[int] = mapped_column(default=0, nullable=False)
    tempo_medio_conclusao_minutos: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    quantidade_problemas: Mapped[int] = mapped_column(default=0, nullable=False)
    taxa_cancelamento: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)

    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="cliente")
    solicitacoes: Mapped[list["SolicitacaoServico"]] = relationship(
        "SolicitacaoServico",
        back_populates="cliente",
    )


class Prestador(Base, TimestampMixin):
    __tablename__ = "prestadores"

    id: Mapped[UUID] = uuid_pk_column()
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    documento: Mapped[str | None] = mapped_column(String(20))
    bio: Mapped[str | None] = mapped_column(Text)
    endereco_principal: Mapped[str | None] = mapped_column(Text)
    bairro: Mapped[str | None] = mapped_column(String(120))
    cidade: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str | None] = mapped_column(String(2))
    media_avaliacao: Mapped[float] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    total_servicos: Mapped[int] = mapped_column(default=0, nullable=False)
    media_notas: Mapped[float] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    total_avaliacoes: Mapped[int] = mapped_column(default=0, nullable=False)
    total_servicos_concluidos: Mapped[int] = mapped_column(default=0, nullable=False)
    tempo_medio_conclusao_minutos: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    quantidade_problemas: Mapped[int] = mapped_column(default=0, nullable=False)
    taxa_cancelamento: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    garantias_acionadas: Mapped[int] = mapped_column(default=0, nullable=False)
    garantias_resolvidas: Mapped[int] = mapped_column(default=0, nullable=False)
    garantias_nao_atendidas: Mapped[int] = mapped_column(default=0, nullable=False)
    tempo_medio_resolucao_garantia_horas: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    reincidencia_garantia: Mapped[int] = mapped_column(default=0, nullable=False)
    aceita_retencao_garantia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_aceite_termos: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    versao_termos: Mapped[str | None] = mapped_column(String(30))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped[Usuario] = relationship("Usuario", back_populates="prestador")
    validacao: Mapped["PrestadorValidacao | None"] = relationship(
        "PrestadorValidacao",
        back_populates="prestador",
    )
    solicitacoes: Mapped[list["SolicitacaoServico"]] = relationship(
        "SolicitacaoServico",
        back_populates="prestador",
    )


class EmpresaFornecedora(Base, TimestampMixin):
    __tablename__ = "empresas_fornecedoras"

    id: Mapped[UUID] = uuid_pk_column()
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    nome_fantasia: Mapped[str] = mapped_column(String(160), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20))
    telefone: Mapped[str | None] = mapped_column(String(20))
    cidade: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str | None] = mapped_column(String(2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped[Usuario | None] = relationship("Usuario", back_populates="empresa_fornecedora")
    materiais: Mapped[list["MaterialServico"]] = relationship(
        "MaterialServico",
        back_populates="empresa_fornecedora",
    )


class PrestadorValidacao(Base, TimestampMixin):
    __tablename__ = "prestador_validacao"

    id: Mapped[UUID] = uuid_pk_column()
    prestador_id: Mapped[UUID] = mapped_column(ForeignKey("prestadores.id"), unique=True, nullable=False)
    status_validacao: Mapped[str] = mapped_column(String(40), default="pendente", nullable=False)
    documento_rg: Mapped[str | None] = mapped_column(Text)
    documento_cpf: Mapped[str | None] = mapped_column(Text)
    selfie_validacao: Mapped[str | None] = mapped_column(Text)
    comprovante_endereco: Mapped[str | None] = mapped_column(Text)
    observacao_admin: Mapped[str | None] = mapped_column(Text)
    data_aprovacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    aprovado_por_admin_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))

    prestador: Mapped[Prestador] = relationship("Prestador", back_populates="validacao")
    aprovado_por_admin: Mapped[Usuario | None] = relationship("Usuario")
