import { useEffect, useState } from "react";

import {
  createCategoriaServico,
  createServico,
  listCategoriasServico,
  listServicos,
  setServicoAtivo,
  updateServico,
} from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, money } from "../utils/format.js";

const emptyForm = {
  id: null,
  categoria_id: "",
  nome: "",
  descricao: "",
  preco_mao_obra: "",
  tempo_estimado_minutos: "",
  precisa_material: false,
  possui_garantia: false,
  dias_garantia: "",
  percentual_retencao_garantia: "",
  dias_liberacao_primeiro_repasse: "",
  descricao_garantia: "",
  regras_garantia: "",
};

const categorySuggestions = [
  {
    nome: "Eletrica",
    descricao: "Chuveiro, tomada, ventilador, resistencia e pequenos reparos eletricos.",
    exemplos: ["Trocar chuveiro", "Trocar tomada", "Instalar ventilador"],
  },
  {
    nome: "Hidraulica",
    descricao: "Torneira, registro, sifao, vazamento e vaso sanitario.",
    exemplos: ["Trocar torneira", "Trocar registro", "Consertar vazamento"],
  },
  {
    nome: "Desentupimento",
    descricao: "Vaso, pia, ralo, esgoto, caixa de gordura e encanamento entupido.",
    exemplos: ["Desentupir vaso", "Desentupir pia", "Desentupir esgoto"],
  },
  {
    nome: "Jardinagem",
    descricao: "Cortar grama, poda simples, limpeza de jardim e manutencao externa.",
    exemplos: ["Cortar grama", "Poda simples", "Limpeza de jardim"],
  },
  {
    nome: "Instalacao",
    descricao: "Suporte de TV, prateleira, varal, cortina e montagem simples.",
    exemplos: ["Instalar suporte TV", "Instalar prateleira", "Instalar varal"],
  },
];

const serviceSuggestions = [
  {
    nome: "Cortar grama",
    categoria: "Jardinagem",
    descricao: "Corte de grama em area residencial, com limpeza simples apos o servico.",
    preco: "120",
    tempo: "90",
    precisaMaterial: false,
  },
  {
    nome: "Desentupir vaso",
    categoria: "Desentupimento",
    descricao: "Desentupimento simples de vaso sanitario residencial, sem quebra de piso ou parede.",
    preco: "180",
    tempo: "90",
    precisaMaterial: false,
  },
  {
    nome: "Desentupir esgoto",
    categoria: "Desentupimento",
    descricao: "Avaliacao e desentupimento inicial de rede de esgoto residencial ou comercial simples.",
    preco: "250",
    tempo: "120",
    precisaMaterial: false,
  },
  {
    nome: "Trocar chuveiro",
    categoria: "Eletrica",
    descricao: "Substituicao de chuveiro residencial, incluindo teste de funcionamento e orientacao ao cliente.",
    preco: "120",
    tempo: "60",
    precisaMaterial: true,
  },
];

export default function ServicosPage() {
  const [data, setData] = useState({ items: [] });
  const [categorias, setCategorias] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [categoriaForm, setCategoriaForm] = useState({ nome: "", descricao: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [showGuide, setShowGuide] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showCategoryTools, setShowCategoryTools] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingCategory, setSavingCategory] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [servicos, categoriasServico] = await Promise.all([
        listServicos({ per_page: 100, ativo: null }),
        listCategoriasServico({ ativo: true }),
      ]);
      setData(servicos);
      setCategorias(categoriasServico || []);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event) {
    event.preventDefault();
    const validation = validateServicoForm(form, categorias);
    setFieldErrors(validation);
    if (Object.keys(validation).length > 0) {
      setError("Confira os campos marcados antes de salvar o servico.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const payload = {
        categoria_id: form.categoria_id,
        nome: form.nome.trim(),
        descricao: form.descricao.trim(),
        preco_mao_obra: Number(form.preco_mao_obra),
        tempo_estimado_minutos: Number(form.tempo_estimado_minutos),
        precisa_material: Boolean(form.precisa_material),
        possui_garantia: Boolean(form.possui_garantia),
        dias_garantia: form.possui_garantia ? Number(form.dias_garantia || 0) : 0,
        percentual_retencao_garantia: form.possui_garantia ? Number(form.percentual_retencao_garantia || 0) : 0,
        dias_liberacao_primeiro_repasse: form.possui_garantia
          ? Number(form.dias_liberacao_primeiro_repasse || 0)
          : 0,
        descricao_garantia: form.possui_garantia ? form.descricao_garantia.trim() || null : null,
        regras_garantia: form.possui_garantia ? form.regras_garantia.trim() || null : null,
      };
      if (form.id) await updateServico(form.id, payload);
      else await createServico(payload);
      setForm(emptyForm);
      setFieldErrors({});
      setShowForm(false);
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function saveCategory(event) {
    event.preventDefault();
    if (!categoriaForm.nome.trim()) {
      setError("Informe o nome da categoria. Ex: Jardinagem, Desentupimento, Hidraulica.");
      return;
    }
    setSavingCategory(true);
    setError("");
    try {
      const categoria = await createCategoriaServico({
        nome: categoriaForm.nome.trim(),
        descricao: categoriaForm.descricao.trim() || null,
      });
      setCategoriaForm({ nome: "", descricao: "" });
      await load();
      setForm((current) => ({ ...current, categoria_id: categoria.id }));
      setShowCategoryTools(false);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSavingCategory(false);
    }
  }

  async function toggle(row) {
    setError("");
    try {
      await setServicoAtivo(row.id, !row.ativo);
      load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    if (fieldErrors[field]) {
      setFieldErrors((current) => {
        const next = { ...current };
        delete next[field];
        return next;
      });
    }
  }

  function startCreate() {
    setError("");
    setFieldErrors({});
    setForm(emptyForm);
    setShowForm(true);
    setShowGuide(false);
  }

  function startEdit(row) {
    setError("");
    setFieldErrors({});
    setShowForm(true);
    setShowGuide(false);
    setForm({
      id: row.id,
      categoria_id: row.categoria_id || "",
      nome: row.nome || "",
      descricao: row.descricao || "",
      preco_mao_obra: String(row.preco_mao_obra ?? ""),
      tempo_estimado_minutos: String(row.tempo_estimado_minutos ?? ""),
      precisa_material: Boolean(row.precisa_material),
      possui_garantia: Boolean(row.possui_garantia),
      dias_garantia: String(row.dias_garantia ?? ""),
      percentual_retencao_garantia: String(row.percentual_retencao_garantia ?? ""),
      dias_liberacao_primeiro_repasse: String(row.dias_liberacao_primeiro_repasse ?? ""),
      descricao_garantia: row.descricao_garantia || "",
      regras_garantia: row.regras_garantia || "",
    });
  }

  function applyServiceSuggestion(suggestion) {
    const categoria = categorias.find((item) => normalize(item.nome) === normalize(suggestion.categoria));
    setError("");
    setFieldErrors({});
    setShowForm(true);
    setShowGuide(false);
    setForm((current) => ({
      ...current,
      id: null,
      categoria_id: categoria?.id || current.categoria_id,
      nome: suggestion.nome,
      descricao: suggestion.descricao,
      preco_mao_obra: suggestion.preco,
      tempo_estimado_minutos: suggestion.tempo,
      precisa_material: suggestion.precisaMaterial,
    }));
    if (!categoria) {
      setShowCategoryTools(true);
      setCategoriaForm({
        nome: suggestion.categoria,
        descricao: `Categoria para servicos como ${suggestion.nome}.`,
      });
      setError(`Crie a categoria ${suggestion.categoria} primeiro. Eu ja preenchi o campo para voce.`);
    }
  }

  function applyCategorySuggestion(suggestion) {
    const existente = categorias.find((item) => normalize(item.nome) === normalize(suggestion.nome));
    if (existente) {
      setForm((current) => ({ ...current, categoria_id: existente.id }));
      setError("");
      return;
    }
    setCategoriaForm({ nome: suggestion.nome, descricao: suggestion.descricao });
    setShowCategoryTools(true);
    setError(`A categoria ${suggestion.nome} ainda nao existe. Confira e clique em Criar categoria.`);
  }

  return (
    <section>
      <Toolbar
        title="Servicos tabelados"
        description="Cadastre os servicos que aparecem no app. Comece simples: categoria, nome, preco e tempo."
      >
          <button type="button" className="primary-button" onClick={startCreate}>
            Novo servico
          </button>
      </Toolbar>
      <ErrorBlock message={error} onRetry={load} />
      <article className="panel service-helper">
        <div>
          <h2>O que voce quer fazer agora?</h2>
          <p className="muted-text">Use um modelo pronto, crie uma categoria ou edite um servico da lista abaixo.</p>
        </div>
        <div className="service-helper-actions">
          <button type="button" className="primary-button" onClick={startCreate}>Criar do zero</button>
          <button type="button" className="ghost-button" onClick={() => setShowGuide((current) => !current)}>
            {showGuide ? "Ocultar ajuda" : "Ver ajuda"}
          </button>
          <button type="button" className="ghost-button" onClick={() => setShowCategoryTools((current) => !current)}>
            {showCategoryTools ? "Ocultar categorias" : "Criar categoria"}
          </button>
        </div>
      </article>
      {showGuide ? (
        <article className="panel guide-panel compact-panel">
          <div>
            <h2>Como cadastrar sem complicar</h2>
            <p>1. Escolha uma categoria. 2. Informe nome, preco e tempo. 3. Salve. Garantia e material podem ficar para depois quando nao forem necessarios.</p>
          </div>
          <button type="button" className="ghost-button" onClick={() => setShowGuide(false)}>Entendi</button>
        </article>
      ) : null}
      {showCategoryTools ? (
      <article className="panel compact-panel">
        <h2>Categorias</h2>
        <p className="muted-text">Categorias ajudam o cliente a encontrar o servico. Exemplos: Jardinagem, Desentupimento, Eletrica.</p>
        <div className="suggestion-row">
          {categorySuggestions.map((item) => (
            <button key={item.nome} type="button" onClick={() => applyCategorySuggestion(item)}>
              <strong>{item.nome}</strong>
              <span>{item.exemplos.join(", ")}</span>
            </button>
          ))}
        </div>
        <form className="category-create-grid" onSubmit={saveCategory}>
          <label className="field-group">
            <span>Nova categoria</span>
            <input
              placeholder="Ex: Desentupimento"
              value={categoriaForm.nome}
              onChange={(event) => setCategoriaForm((current) => ({ ...current, nome: event.target.value }))}
            />
          </label>
          <label className="field-group">
            <span>Descricao simples</span>
            <input
              placeholder="Ex: vaso, pia, ralo e esgoto"
              value={categoriaForm.descricao}
              onChange={(event) => setCategoriaForm((current) => ({ ...current, descricao: event.target.value }))}
            />
          </label>
          <button className="primary-button" disabled={savingCategory}>
            {savingCategory ? "Criando..." : "Criar categoria"}
          </button>
        </form>
      </article>
      ) : null}
      <article className="panel compact-panel">
        <h2>Modelos rapidos de servico</h2>
        <p className="muted-text">Clique em um exemplo para preencher o formulario. Voce pode alterar tudo antes de salvar.</p>
        <div className="quick-service-grid">
          {serviceSuggestions.map((item) => (
            <button key={item.nome} type="button" onClick={() => applyServiceSuggestion(item)}>
              <strong>{item.nome}</strong>
              <span>{item.categoria} | R$ {item.preco} | {item.tempo} min</span>
            </button>
          ))}
        </div>
      </article>
      {showForm ? (
        <form className="panel service-editor" onSubmit={save}>
          <div className="editor-header">
            <div>
              <h2>{form.id ? "Editar servico" : "Novo servico"}</h2>
              <p className="muted-text">Preencha somente o essencial. Depois voce pode voltar e ajustar garantia, material e regras.</p>
            </div>
            <button type="button" className="ghost-button" onClick={() => { setForm(emptyForm); setFieldErrors({}); setShowForm(false); }}>
              Cancelar
            </button>
          </div>
          <div className="form-grid">
            <label className="field-group">
              <span>Categoria</span>
              <select
                className={fieldErrors.categoria_id ? "input-error" : ""}
                value={form.categoria_id}
                onChange={(e) => updateField("categoria_id", e.target.value)}
              >
                <option value="">Selecione uma categoria</option>
                {categorias.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nome}
                  </option>
                ))}
              </select>
              {fieldErrors.categoria_id ? <small className="field-error">{fieldErrors.categoria_id}</small> : null}
              {categorias.length === 0 ? <small className="field-error">Crie uma categoria para liberar este campo.</small> : null}
            </label>
            <label className="field-group">
              <span>Nome do servico</span>
              <input
                className={fieldErrors.nome ? "input-error" : ""}
                placeholder="Ex: Cortar grama"
                value={form.nome}
                onChange={(e) => updateField("nome", e.target.value)}
              />
              {fieldErrors.nome ? <small className="field-error">{fieldErrors.nome}</small> : null}
            </label>
            <label className="field-group">
              <span>Preco mao de obra</span>
              <input
                className={fieldErrors.preco_mao_obra ? "input-error" : ""}
                placeholder="Ex: 120"
                type="number"
                min="0"
                step="0.01"
                value={form.preco_mao_obra}
                onChange={(e) => updateField("preco_mao_obra", e.target.value)}
              />
              {fieldErrors.preco_mao_obra ? <small className="field-error">{fieldErrors.preco_mao_obra}</small> : null}
            </label>
            <label className="field-group">
              <span>Tempo estimado</span>
              <input
                className={fieldErrors.tempo_estimado_minutos ? "input-error" : ""}
                placeholder="Minutos"
                type="number"
                min="1"
                step="1"
                value={form.tempo_estimado_minutos}
                onChange={(e) => updateField("tempo_estimado_minutos", e.target.value)}
              />
              {fieldErrors.tempo_estimado_minutos ? (
                <small className="field-error">{fieldErrors.tempo_estimado_minutos}</small>
              ) : null}
            </label>
            <label className="field-group textarea-field">
              <span>Descricao</span>
              <textarea
                className={fieldErrors.descricao ? "input-error" : ""}
                placeholder="Explique em linguagem simples o que esta incluido no servico."
                value={form.descricao}
                onChange={(e) => updateField("descricao", e.target.value)}
              />
              {fieldErrors.descricao ? <small className="field-error">{fieldErrors.descricao}</small> : null}
            </label>
            <label className="check-row">
              <input type="checkbox" checked={form.precisa_material} onChange={(e) => updateField("precisa_material", e.target.checked)} />
              Precisa material
            </label>
            <label className="check-row">
              <input type="checkbox" checked={form.possui_garantia} onChange={(e) => updateField("possui_garantia", e.target.checked)} />
              Configurar garantia
            </label>
          </div>
          {form.possui_garantia ? (
            <div className="form-grid warranty-section">
              <label className="field-group">
                <span>Dias de garantia</span>
                <input
                  className={fieldErrors.dias_garantia ? "input-error" : ""}
                  type="number"
                  min="1"
                  step="1"
                  value={form.dias_garantia}
                  onChange={(e) => updateField("dias_garantia", e.target.value)}
                />
                {fieldErrors.dias_garantia ? <small className="field-error">{fieldErrors.dias_garantia}</small> : null}
              </label>
              <label className="field-group">
                <span>Retencao da garantia (%)</span>
                <input
                  className={fieldErrors.percentual_retencao_garantia ? "input-error" : ""}
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  value={form.percentual_retencao_garantia}
                  onChange={(e) => updateField("percentual_retencao_garantia", e.target.value)}
                />
                {fieldErrors.percentual_retencao_garantia ? (
                  <small className="field-error">{fieldErrors.percentual_retencao_garantia}</small>
                ) : null}
              </label>
              <label className="field-group">
                <span>Dias para primeiro repasse</span>
                <input
                  className={fieldErrors.dias_liberacao_primeiro_repasse ? "input-error" : ""}
                  type="number"
                  min="0"
                  step="1"
                  value={form.dias_liberacao_primeiro_repasse}
                  onChange={(e) => updateField("dias_liberacao_primeiro_repasse", e.target.value)}
                />
                {fieldErrors.dias_liberacao_primeiro_repasse ? (
                  <small className="field-error">{fieldErrors.dias_liberacao_primeiro_repasse}</small>
                ) : null}
              </label>
              <label className="field-group textarea-field">
                <span>Descricao da garantia</span>
                <textarea
                  placeholder="Explique o que a garantia cobre."
                  value={form.descricao_garantia}
                  onChange={(e) => updateField("descricao_garantia", e.target.value)}
                />
              </label>
              <label className="field-group textarea-field">
                <span>Regras da garantia</span>
                <textarea
                  placeholder="Ex: garantia valida apenas para servicos feitos dentro da plataforma."
                  value={form.regras_garantia}
                  onChange={(e) => updateField("regras_garantia", e.target.value)}
                />
              </label>
            </div>
          ) : null}
          <div className="editor-actions">
            <button className="primary-button" disabled={saving}>
              {saving ? "Salvando..." : form.id ? "Salvar alteracoes" : "Criar servico"}
            </button>
            <button type="button" className="ghost-button" onClick={() => { setForm(emptyForm); setFieldErrors({}); setShowForm(false); }}>
              Cancelar
            </button>
          </div>
        </form>
      ) : null}
      {loading ? <LoadingBlock message="Carregando servicos..." /> : (
        <DataTable
          rows={data.items || []}
          columns={[
            { key: "nome", label: "Servico" },
            {
              key: "categoria_id",
              label: "Categoria",
              render: (row) => categoryName(row.categoria_id, categorias),
            },
            { key: "descricao", label: "Descricao" },
            { key: "preco_mao_obra", label: "Preco", render: (row) => money(row.preco_mao_obra) },
            { key: "tempo_estimado_minutos", label: "Tempo", render: (row) => `${row.tempo_estimado_minutos} min` },
            {
              key: "garantia",
              label: "Garantia",
              render: (row) => row.possui_garantia ? `${row.dias_garantia} dias / ${row.percentual_retencao_garantia}%` : "Sem garantia",
            },
            { key: "ativo", label: "Status", render: (row) => <StatusBadge value={row.ativo ? "ativo" : "inativo"} /> },
            {
              key: "actions",
              label: "Acoes",
              render: (row) => (
                <div className="row-actions">
                  <button onClick={() => startEdit(row)}>Editar</button>
                  <button onClick={() => toggle(row)}>{row.ativo ? "Desativar" : "Ativar"}</button>
                </div>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}

function validateServicoForm(form, categorias) {
  const errors = {};
  const categoriaExiste = categorias.some((categoria) => categoria.id === form.categoria_id);
  if (!form.categoria_id || !categoriaExiste) {
    errors.categoria_id = "Escolha uma categoria da lista.";
  }
  if (!form.nome.trim()) {
    errors.nome = "Nome do servico obrigatorio.";
  } else if (form.nome.trim().length < 3) {
    errors.nome = "Use pelo menos 3 caracteres.";
  }
  if (!form.descricao.trim()) {
    errors.descricao = "Descricao obrigatoria.";
  } else if (form.descricao.trim().length < 10) {
    errors.descricao = "Descreva com pelo menos 10 caracteres.";
  }
  const preco = Number(form.preco_mao_obra);
  if (form.preco_mao_obra === "" || Number.isNaN(preco) || preco < 0) {
    errors.preco_mao_obra = "Informe um preco valido.";
  }
  const tempo = Number(form.tempo_estimado_minutos);
  if (form.tempo_estimado_minutos === "" || Number.isNaN(tempo) || tempo <= 0) {
    errors.tempo_estimado_minutos = "Informe um tempo maior que zero.";
  }
  if (form.possui_garantia) {
    const diasGarantia = Number(form.dias_garantia);
    const percentualRetencao = Number(form.percentual_retencao_garantia);
    const diasPrimeiroRepasse = Number(form.dias_liberacao_primeiro_repasse || 0);
    if (form.dias_garantia === "" || Number.isNaN(diasGarantia) || diasGarantia <= 0) {
      errors.dias_garantia = "Informe os dias de garantia.";
    }
    if (
      form.percentual_retencao_garantia === "" ||
      Number.isNaN(percentualRetencao) ||
      percentualRetencao < 0 ||
      percentualRetencao > 100
    ) {
      errors.percentual_retencao_garantia = "Informe uma retencao entre 0 e 100%.";
    }
    if (Number.isNaN(diasPrimeiroRepasse) || diasPrimeiroRepasse < 0) {
      errors.dias_liberacao_primeiro_repasse = "Informe zero ou mais dias.";
    }
  }
  return errors;
}

function categoryName(categoriaId, categorias) {
  return categorias.find((categoria) => categoria.id === categoriaId)?.nome || "Categoria nao encontrada";
}

function normalize(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}
