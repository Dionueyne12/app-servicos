from pydantic import BaseModel, Field

from app.pagination import PaginationMeta


class CadastroUsuarioRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: str = Field(max_length=180)
    telefone: str = Field(min_length=10, max_length=20)
    senha: str = Field(min_length=8, max_length=128)
    tipo_usuario: str = Field(pattern="^(cliente|prestador)$")
    endereco: str = Field(min_length=5, max_length=500)
    bairro: str = Field(min_length=2, max_length=120)
    documento: str | None = Field(default=None, max_length=20)
    cidade: str = Field(min_length=2, max_length=120)
    estado: str = Field(min_length=2, max_length=2)


class CadastroPerfilRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: str = Field(max_length=180)
    telefone: str = Field(min_length=10, max_length=20)
    senha: str = Field(min_length=8, max_length=128)
    endereco: str = Field(min_length=5, max_length=500)
    bairro: str = Field(min_length=2, max_length=120)
    documento: str | None = Field(default=None, max_length=20)
    cidade: str = Field(min_length=2, max_length=120)
    estado: str = Field(min_length=2, max_length=2)


class LoginRequest(BaseModel):
    email: str = Field(max_length=180)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str
    tipo_usuario: str
    ativo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class AuthMeResponse(BaseModel):
    usuario: UsuarioResponse
    cliente_id: str | None = None
    prestador_id: str | None = None
    status_validacao_prestador: str | None = None


class AdminPrestadorRejeitarRequest(BaseModel):
    observacao_admin: str = Field(min_length=3, max_length=1000)


class CategoriaServicoResponse(BaseModel):
    id: str
    nome: str
    descricao: str | None = None
    ativo: bool


class CategoriaServicoCreateRequest(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    descricao: str | None = Field(default=None, max_length=1000)


class CategoriaServicoUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    descricao: str | None = Field(default=None, max_length=1000)


class ServicoTabeladoCreateRequest(BaseModel):
    categoria_id: str
    nome: str = Field(min_length=3, max_length=160)
    descricao: str = Field(min_length=10, max_length=1000)
    preco_mao_obra: float = Field(ge=0)
    tempo_estimado_minutos: int = Field(gt=0)
    precisa_material: bool = False
    possui_garantia: bool = False
    dias_garantia: int = Field(default=0, ge=0)
    percentual_retencao_garantia: float = Field(default=0, ge=0, le=100)
    dias_liberacao_primeiro_repasse: int = Field(default=0, ge=0)
    descricao_garantia: str | None = Field(default=None, max_length=1000)
    regras_garantia: str | None = Field(default=None, max_length=2000)


class ServicoTabeladoUpdateRequest(BaseModel):
    categoria_id: str | None = None
    nome: str | None = Field(default=None, min_length=3, max_length=160)
    descricao: str | None = Field(default=None, min_length=10, max_length=1000)
    preco_mao_obra: float | None = Field(default=None, ge=0)
    tempo_estimado_minutos: int | None = Field(default=None, gt=0)
    precisa_material: bool | None = None
    possui_garantia: bool | None = None
    dias_garantia: int | None = Field(default=None, ge=0)
    percentual_retencao_garantia: float | None = Field(default=None, ge=0, le=100)
    dias_liberacao_primeiro_repasse: int | None = Field(default=None, ge=0)
    descricao_garantia: str | None = Field(default=None, max_length=1000)
    regras_garantia: str | None = Field(default=None, max_length=2000)


class ServicoTabeladoResponse(BaseModel):
    id: str
    categoria_id: str
    nome: str
    descricao: str
    preco_mao_obra: float
    tempo_estimado_minutos: int
    precisa_material: bool
    ativo: bool
    possui_garantia: bool
    dias_garantia: int
    percentual_retencao_garantia: float
    dias_liberacao_primeiro_repasse: int
    descricao_garantia: str | None
    regras_garantia: str | None


class ServicoTabeladoPaginatedResponse(BaseModel):
    items: list[ServicoTabeladoResponse]
    meta: PaginationMeta


class SolicitacaoServicoCreateRequest(BaseModel):
    cliente_id: str
    tipo_servico: str = Field(pattern="^(tabelado|personalizado)$")
    servico_tabelado_id: str | None = None
    categoria_id: str | None = None
    descricao_problema: str = Field(min_length=10, max_length=1000)
    endereco: str = Field(min_length=5, max_length=500)
    urgencia: str = Field(default="normal", pattern="^(baixa|normal|alta)$")
    melhor_horario: str | None = Field(default=None, max_length=120)
    observacoes: str | None = Field(default=None, max_length=1000)
    valor_mao_obra: float | None = Field(default=None, ge=0)
    tempo_estimado: int | None = Field(default=None, gt=0)
    tipo_material: str = Field(
        pattern="^(cliente_fornece_material|prestador_providencia_material|material_indefinido)$"
    )


class SolicitacaoServicoUpdateRequest(BaseModel):
    tipo_servico: str | None = Field(default=None, pattern="^(tabelado|personalizado)$")
    servico_tabelado_id: str | None = None
    categoria_id: str | None = None
    descricao_problema: str | None = Field(default=None, min_length=10, max_length=1000)
    endereco: str | None = Field(default=None, min_length=5, max_length=500)
    urgencia: str | None = Field(default=None, pattern="^(baixa|normal|alta)$")
    melhor_horario: str | None = Field(default=None, max_length=120)
    observacoes: str | None = Field(default=None, max_length=1000)
    valor_mao_obra: float | None = Field(default=None, ge=0)
    tempo_estimado: int | None = Field(default=None, gt=0)
    tipo_material: str | None = Field(
        default=None,
        pattern="^(cliente_fornece_material|prestador_providencia_material|material_indefinido)$",
    )


class MaterialServicoResponse(BaseModel):
    id: str | None = None
    tipo_material: str
    descricao_material: str | None = None
    valor_material_estimado: float | None = None
    necessita_aprovacao_cliente: bool | None = None
    aprovado_pelo_cliente: bool | None = None
    status_material: str | None = None
    observacao_cliente: str | None = None


class GarantiaResumoResponse(BaseModel):
    id: str
    status_garantia: str
    data_inicio_garantia: str
    data_fim_garantia: str
    valor_retido: float
    valor_liberado_inicial: float
    percentual_retencao: float
    bloqueio_repasse: bool


class SolicitacaoServicoResponse(BaseModel):
    id: str
    cliente_id: str
    prestador_id: str | None
    tipo_servico: str
    servico_tabelado_id: str | None
    categoria_id: str | None
    descricao_problema: str
    endereco: str
    urgencia: str
    melhor_horario: str | None
    observacoes: str | None
    valor_mao_obra: float | None
    valor_material_total: float
    valor_total_estimado: float
    tempo_estimado: int | None
    status: str
    material: MaterialServicoResponse | None
    garantia: GarantiaResumoResponse | None = None


class SolicitacaoServicoPaginatedResponse(BaseModel):
    items: list[SolicitacaoServicoResponse]
    meta: PaginationMeta


class SolicitacaoStatusUpdateRequest(BaseModel):
    status: str = Field(
        pattern=(
            "^(aceito|aguardando_avaliacao_material|aguardando_aprovacao_cliente|"
            "material_aprovado|em_andamento|aguardando_confirmacao_cliente|"
            "concluido|cancelado|em_analise)$"
        )
    )


class SolicitacaoProblemaRequest(BaseModel):
    observacao_problema: str = Field(min_length=10, max_length=1000)


class GarantiaAcionamentoRequest(BaseModel):
    descricao_problema: str = Field(min_length=10, max_length=1000)
    observacao_cliente: str | None = Field(default=None, max_length=1000)
    fotos: list[str] | None = Field(default=None, max_length=10)


class GarantiaAdminAcaoRequest(BaseModel):
    observacao_admin: str | None = Field(default=None, max_length=1000)
    procedente: bool | None = None


class GarantiaServicoResponse(BaseModel):
    id: str
    solicitacao_id: str
    prestador_id: str
    cliente_id: str
    servico_tabelado_id: str | None
    pagamento_simulado_id: str | None
    pagamento_id: str | None
    data_inicio_garantia: str
    data_fim_garantia: str
    status_garantia: str
    valor_retido: float
    valor_liberado_inicial: float
    percentual_retencao: float
    dias_garantia: int
    dias_liberacao_primeiro_repasse: int
    descricao_problema: str | None
    observacao_cliente: str | None
    observacao_admin: str | None
    bloqueio_repasse: bool
    procedente: bool | None
    data_acionamento: str | None
    data_resolucao: str | None
    created_at: str


class GarantiaServicoPaginatedResponse(BaseModel):
    items: list[GarantiaServicoResponse]
    meta: PaginationMeta


class MaterialServicoCreateRequest(BaseModel):
    empresa_fornecedora_id: str | None = None
    descricao_material: str = Field(min_length=3, max_length=1000)
    valor_estimado: float = Field(gt=0)
    necessita_aprovacao_cliente: bool = True


class MaterialClienteAcaoRequest(BaseModel):
    observacao_cliente: str | None = Field(default=None, max_length=1000)


class AvaliacaoCreateRequest(BaseModel):
    nota: int = Field(ge=1, le=5)
    comentario: str | None = Field(default=None, max_length=1000)


class AvaliacaoResponse(BaseModel):
    id: str
    solicitacao_id: str
    avaliador_usuario_id: str
    avaliado_usuario_id: str
    tipo_avaliacao: str
    nota: int
    comentario: str | None
    created_at: str


class AvaliacaoPaginatedResponse(BaseModel):
    items: list[AvaliacaoResponse]
    meta: PaginationMeta


class MensagemSolicitacaoCreateRequest(BaseModel):
    tipo_mensagem: str = Field(default="texto", pattern="^(texto|imagem|sistema|alerta|comprovante)$")
    mensagem: str = Field(min_length=1, max_length=2000)
    arquivo_url: str | None = Field(default=None, max_length=1000)


class MensagemSolicitacaoResponse(BaseModel):
    id: str
    solicitacao_id: str
    remetente_usuario_id: str
    destinatario_usuario_id: str
    tipo_mensagem: str
    mensagem: str
    arquivo_url: str | None
    visualizada: bool
    data_visualizacao: str | None
    created_at: str


class MensagemSolicitacaoPaginatedResponse(BaseModel):
    items: list[MensagemSolicitacaoResponse]
    meta: PaginationMeta
    nao_lidas: int


class NotificacaoResponse(BaseModel):
    id: str
    usuario_id: str
    solicitacao_id: str | None
    tipo_notificacao: str
    titulo: str
    mensagem: str
    lida: bool
    data_leitura: str | None
    prioridade: str
    canal: str
    created_at: str


class NotificacaoPaginatedResponse(BaseModel):
    items: list[NotificacaoResponse]
    meta: PaginationMeta
    nao_lidas: int


class RepasseResponse(BaseModel):
    id: str
    pagamento_id: str
    destinatario_usuario_id: str | None
    empresa_fornecedora_id: str | None
    tipo_repasse: str
    valor: float
    status_repasse: str
    created_at: str


class PagamentoSimuladoResponse(BaseModel):
    id: str
    solicitacao_id: str
    valor_mao_obra: float
    valor_material: float
    valor_comissao: float
    valor_prestador: float
    valor_empresa: float
    valor_total: float
    status_pagamento: str
    repasses: list[RepasseResponse]
    created_at: str


class PagamentoSimuladoPaginatedResponse(BaseModel):
    items: list[PagamentoSimuladoResponse]
    meta: PaginationMeta


class RepassePaginatedResponse(BaseModel):
    items: list[RepasseResponse]
    meta: PaginationMeta


class PagamentoCreateRequest(BaseModel):
    solicitacao_id: str
    metodo_pagamento: str = Field(
        default="pix",
        pattern="^(pix|cartao|boleto|carteira_interna|pagamento_futuro)$",
    )
    comprovante_pagamento: str | None = Field(default=None, max_length=1000)


class PagamentoResponse(BaseModel):
    id: str
    solicitacao_id: str
    cliente_id: str
    prestador_id: str
    valor_mao_obra: float
    valor_material: float
    valor_total: float
    valor_comissao_plataforma: float
    valor_prestador: float
    valor_fornecedor: float
    status_pagamento: str
    metodo_pagamento: str
    data_pagamento: str | None
    data_liberacao_repasse: str | None
    comprovante_pagamento: str | None
    created_at: str


class PagamentoPaginatedResponse(BaseModel):
    items: list[PagamentoResponse]
    meta: PaginationMeta


class CarteiraUsuarioResponse(BaseModel):
    usuario_id: str
    saldo_disponivel: float
    saldo_pendente: float
    saldo_bloqueado: float
    total_recebido: float
    total_movimentado: float


class MovimentacaoCarteiraResponse(BaseModel):
    id: str
    usuario_id: str
    pagamento_id: str | None
    tipo_movimentacao: str
    valor: float
    descricao: str | None
    saldo_disponivel_apos: float
    saldo_pendente_apos: float
    saldo_bloqueado_apos: float
    created_at: str


class MovimentacaoCarteiraPaginatedResponse(BaseModel):
    items: list[MovimentacaoCarteiraResponse]
    meta: PaginationMeta


class FotoServicoResponse(BaseModel):
    id: str
    solicitacao_id: str
    usuario_id: str
    caminho_arquivo: str
    nome_original: str
    mime_type: str
    tamanho_bytes: int
    tipo_foto: str
    descricao: str | None
    created_at: str
