import { useEffect, useMemo, useState } from "react";

import {
  createCategoriaServico,
  createServico,
  listCategoriasServico,
  listServicos,
  setCategoriaServicoAtivo,
  setServicoAtivo,
  updateCategoriaServico,
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
  preco_mao_obra: "",
  tempo_minimo: "",
  tempo_maximo: "",
  unidade_tempo: "minutos",
  precisa_material: false,
  material_padrao: "",
  descricao: "",
  observacao_interna: "",
  ativo: true,
  possui_garantia: false,
  dias_garantia: "",
  percentual_retencao_garantia: "",
  dias_liberacao_primeiro_repasse: "",
};

const quickServices = [
  { nome: "Cortar grama", categoria: "Jardinagem", preco: "120", tempo: "90", material: false },
  { nome: "Desentupir vaso", categoria: "Desentupimento", preco: "180", tempo: "90", material: false },
  { nome: "Desentupir esgoto", categoria: "Desentupimento", preco: "250", tempo: "120", material: false },
  { nome: "Trocar chuveiro", categoria: "Eletrica", preco: "120", tempo: "60", material: true },
];

const defaultCategories = [
  "Eletrica",
  "Hidraulica",
  "Desentupimento",
  "Jardinagem",
  "Instalacao",
  "Limpeza",
  "Manutencao geral",
];

export default function ServicosPage() {
  const [data, setData] = useState({ items: [] });
  const [categorias, setCategorias] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [categoryForm, setCategoryForm] = useState({ nome: "", descricao: "" });
  const [editingCategoryId, setEditingCategoryId] = useState(null);
  const [editingCategory, setEditingCategory] = useState({ nome: "", descricao: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingCategory, setSavingCategory] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const servicos = data.items || [];
  const serviceCountByCategory = useMemo(() => {
    const counts = {};
    servicos.forEach((servico) => {
      counts[servico.categoria_id] = (counts[servico.categoria_id] || 0) + 1;
    });
    return counts;
  }, [servicos]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [servicosResponse, categoriasResponse] = await Promise.all([
        listServicos({ per_page: 100, ativo: null }),
        listCategoriasServico({ ativo: null }),
      ]);
      setData(servicosResponse);
      setCategorias(categoriasResponse || []);
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
    const validation = validateServicoForm(form);
    setFieldErrors(validation);
    setSuccess("");
    if (Object.keys(validation).length > 0) {
      setError("Confira os campos marcados antes de salvar o servico.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const descricao = buildDescription(form);
      const tempo = toMinutes(Number(form.tempo_maximo), form.unidade_tempo);
      const payload = {
        categoria_id: form.categoria_id,
        nome: form.nome.trim(),
        descricao,
        preco_mao_obra: Number(form.preco_mao_obra),
        tempo_estimado_minutos: tempo,
        precisa_material: Boolean(form.precisa_material),
        possui_garantia: Boolean(form.possui_garantia),
        dias_garantia: form.possui_garantia ? Number(form.dias_garantia || 0) : 0,
        percentual_retencao_garantia: form.possui_garantia ? Number(form.percentual_retencao_garantia || 0) : 0,
        dias_liberacao_primeiro_repasse: form.possui_garantia
          ? Number(form.dias_liberacao_primeiro_repasse || 0)
          : 0,
      };

      const saved = form.id ? await updateServico(form.id, payload) : await createServico(payload);
      if (Boolean(saved.ativo) !== Boolean(form.ativo)) {
        await setServicoAtivo(saved.id, Boolean(form.ativo));
      }
      setForm(emptyForm);
      setFieldErrors({});
      setSuccess(form.id ? "Servico atualizado com sucesso." : "Servico cadastrado com sucesso.");
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function saveCategory(event) {
    event.preventDefault();
    if (!categoryForm.nome.trim()) {
      setError("Informe o nome da categoria.");
      return;
    }
    setSavingCategory(true);
    setError("");
    setSuccess("");
    try {
      await createCategoriaServico({
        nome: categoryForm.nome.trim(),
        descricao: categoryForm.descricao.trim() || null,
      });
      setCategoryForm({ nome: "", descricao: "" });
      setSuccess("Categoria criada com sucesso.");
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSavingCategory(false);
    }
  }

  async function saveCategoryEdit(categoria) {
    if (!editingCategory.nome.trim()) {
      setError("Informe o nome da categoria.");
      return;
    }
    setError("");
    setSuccess("");
    try {
      await updateCategoriaServico(categoria.id, {
        nome: editingCategory.nome.trim(),
        descricao: editingCategory.descricao.trim() || null,
      });
      setEditingCategoryId(null);
      setEditingCategory({ nome: "", descricao: "" });
      setSuccess("Categoria atualizada com sucesso.");
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  async function toggleCategory(categoria) {
    setError("");
    setSuccess("");
    try {
      await setCategoriaServicoAtivo(categoria.id, !categoria.ativo);
      setSuccess(categoria.ativo ? "Categoria desativada." : "Categoria ativada.");
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  async function toggleService(row) {
    setError("");
    setSuccess("");
    try {
      await setServicoAtivo(row.id, !row.ativo);
      setSuccess(row.ativo ? "Servico desativado." : "Servico ativado.");
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    setSuccess("");
    if (fieldErrors[field]) {
      setFieldErrors((current) => {
        const next = { ...current };
        delete next[field];
        return next;
      });
    }
  }

  function startEdit(row) {
    setError("");
    setSuccess("");
    setFieldErrors({});
    setForm({
      ...emptyForm,
      id: row.id,
      categoria_id: row.categoria_id || "",
      nome: row.nome || "",
      preco_mao_obra: String(row.preco_mao_obra ?? ""),
      tempo_minimo: String(row.tempo_estimado_minutos ?? ""),
      tempo_maximo: String(row.tempo_estimado_minutos ?? ""),
      unidade_tempo: "minutos",
      precisa_material: Boolean(row.precisa_material),
      descricao: row.descricao || "",
      ativo: Boolean(row.ativo),
      possui_garantia: Boolean(row.possui_garantia),
      dias_garantia: String(row.dias_garantia ?? ""),
      percentual_retencao_garantia: String(row.percentual_retencao_garantia ?? ""),
      dias_liberacao_primeiro_repasse: String(row.dias_liberacao_primeiro_repasse ?? ""),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function applyQuickService(item) {
    const categoria = categorias.find((categoriaItem) => normalize(categoriaItem.nome) === normalize(item.categoria));
    setForm({
      ...emptyForm,
      categoria_id: categoria?.id || "",
      nome: item.nome,
      preco_mao_obra: item.preco,
      tempo_minimo: item.tempo,
      tempo_maximo: item.tempo,
      precisa_material: item.material,
      descricao: `${item.nome} residencial com avaliacao do prestador antes da execucao.`,
    });
    if (!categoria) {
      setCategoryForm({ nome: item.categoria, descricao: `Categoria para servicos como ${item.nome}.` });
      setError(`Crie a categoria ${item.categoria} primeiro. O campo ja foi preenchido abaixo.`);
    } else {
      setError("");
    }
  }

  return (
    <section>
      <Toolbar
        title="Servicos tabelados"
        description="Organize categorias, precos e tempos dos servicos que aparecem no app."
      />
      <ErrorBlock message={error} onRetry={load} />
      {success ? <div className="success-block">{success}</div> : null}

      <article className="panel service-form-card">
        <div className="card-heading">
          <div>
            <h2>{form.id ? "Editar servico tabelado" : "Cadastrar servico tabelado"}</h2>
            <p>Preencha os campos principais. O restante pode ser ajustado depois.</p>
          </div>
          {form.id ? (
            <button type="button" className="small-button neutral" onClick={() => { setForm(emptyForm); setFieldErrors({}); }}>
              Cancelar
            </button>
          ) : null}
        </div>

        <div className="quick-service-grid service-presets">
          {quickServices.map((item) => (
            <button key={item.nome} type="button" onClick={() => applyQuickService(item)}>
              <strong>{item.nome}</strong>
              <span>{item.categoria} | R$ {item.preco}</span>
            </button>
          ))}
        </div>

        <form className="service-form-grid" onSubmit={save}>
          <label className="field-group">
            <span>Categoria *</span>
            <select
              className={fieldErrors.categoria_id ? "input-error" : ""}
              value={form.categoria_id}
              onChange={(event) => updateField("categoria_id", event.target.value)}
            >
              <option value="">Selecione uma categoria</option>
              {categorias.filter((categoria) => categoria.ativo).map((categoria) => (
                <option key={categoria.id} value={categoria.id}>{categoria.nome}</option>
              ))}
            </select>
            {fieldErrors.categoria_id ? <small className="field-error">{fieldErrors.categoria_id}</small> : null}
          </label>

          <label className="field-group">
            <span>Nome do servico *</span>
            <input
              className={fieldErrors.nome ? "input-error" : ""}
              placeholder="Ex: Cortar grama"
              value={form.nome}
              onChange={(event) => updateField("nome", event.target.value)}
            />
            {fieldErrors.nome ? <small className="field-error">{fieldErrors.nome}</small> : null}
          </label>

          <label className="field-group">
            <span>Preco base da mao de obra *</span>
            <input
              className={fieldErrors.preco_mao_obra ? "input-error" : ""}
              type="number"
              min="0"
              step="0.01"
              placeholder="Ex: 120"
              value={form.preco_mao_obra}
              onChange={(event) => updateField("preco_mao_obra", event.target.value)}
            />
            {fieldErrors.preco_mao_obra ? <small className="field-error">{fieldErrors.preco_mao_obra}</small> : null}
          </label>

          <label className="field-group">
            <span>Tempo minimo *</span>
            <input
              className={fieldErrors.tempo_minimo ? "input-error" : ""}
              type="number"
              min="1"
              step="1"
              placeholder="Ex: 60"
              value={form.tempo_minimo}
              onChange={(event) => updateField("tempo_minimo", event.target.value)}
            />
            {fieldErrors.tempo_minimo ? <small className="field-error">{fieldErrors.tempo_minimo}</small> : null}
          </label>

          <label className="field-group">
            <span>Tempo maximo *</span>
            <input
              className={fieldErrors.tempo_maximo ? "input-error" : ""}
              type="number"
              min="1"
              step="1"
              placeholder="Ex: 90"
              value={form.tempo_maximo}
              onChange={(event) => updateField("tempo_maximo", event.target.value)}
            />
            {fieldErrors.tempo_maximo ? <small className="field-error">{fieldErrors.tempo_maximo}</small> : null}
          </label>

          <label className="field-group">
            <span>Unidade de tempo</span>
            <select value={form.unidade_tempo} onChange={(event) => updateField("unidade_tempo", event.target.value)}>
              <option value="minutos">Minutos</option>
              <option value="horas">Horas</option>
              <option value="dias">Dias</option>
            </select>
          </label>

          <label className="field-group">
            <span>Status</span>
            <select value={form.ativo ? "ativo" : "inativo"} onChange={(event) => updateField("ativo", event.target.value === "ativo")}>
              <option value="ativo">Ativo</option>
              <option value="inativo">Inativo</option>
            </select>
          </label>

          <label className="check-row service-check">
            <input
              type="checkbox"
              checked={form.precisa_material}
              onChange={(event) => updateField("precisa_material", event.target.checked)}
            />
            Precisa de material?
          </label>

          {form.precisa_material ? (
            <label className="field-group form-wide">
              <span>Qual material normalmente e necessario?</span>
              <input
                placeholder="Ex: chuveiro novo, fita veda rosca, tomada, parafusos"
                value={form.material_padrao}
                onChange={(event) => updateField("material_padrao", event.target.value)}
              />
            </label>
          ) : null}

          <label className="field-group form-wide">
            <span>Descricao para o cliente *</span>
            <textarea
              className={fieldErrors.descricao ? "input-error" : ""}
              placeholder="Explique de forma simples o que esta incluido no servico."
              value={form.descricao}
              onChange={(event) => updateField("descricao", event.target.value)}
            />
            {fieldErrors.descricao ? <small className="field-error">{fieldErrors.descricao}</small> : null}
          </label>

          <label className="field-group form-wide">
            <span>Observacao interna para o prestador</span>
            <textarea
              placeholder="Ex: verificar voltagem antes de instalar, levar ferramentas basicas."
              value={form.observacao_interna}
              onChange={(event) => updateField("observacao_interna", event.target.value)}
            />
          </label>

          <div className="form-actions-row">
            <button className="primary-button" disabled={saving}>
              {saving ? "Salvando..." : form.id ? "Salvar" : "Cadastrar servico"}
            </button>
            <button type="button" className="small-button neutral" onClick={() => { setForm(emptyForm); setFieldErrors({}); }}>
              Cancelar
            </button>
          </div>
        </form>
      </article>

      <article className="panel categories-card">
        <div className="card-heading">
          <div>
            <h2>Categorias cadastradas</h2>
            <p>Use categorias para organizar os servicos no app.</p>
          </div>
        </div>

        <form className="category-create-grid" onSubmit={saveCategory}>
          <label className="field-group">
            <span>Nova categoria</span>
            <input
              placeholder="Ex: Desentupimento"
              value={categoryForm.nome}
              onChange={(event) => setCategoryForm((current) => ({ ...current, nome: event.target.value }))}
              list="category-suggestions"
            />
            <datalist id="category-suggestions">
              {defaultCategories.map((categoria) => <option key={categoria} value={categoria} />)}
            </datalist>
          </label>
          <label className="field-group">
            <span>Descricao simples</span>
            <input
              placeholder="Ex: vaso, pia, ralo e esgoto"
              value={categoryForm.descricao}
              onChange={(event) => setCategoryForm((current) => ({ ...current, descricao: event.target.value }))}
            />
          </label>
          <button className="primary-button" disabled={savingCategory}>
            {savingCategory ? "Criando..." : "Criar categoria"}
          </button>
        </form>

        <div className="category-list">
          {categorias.map((categoria) => {
            const editing = editingCategoryId === categoria.id;
            return (
              <div className="category-row" key={categoria.id}>
                <div className="category-main">
                  {editing ? (
                    <>
                      <input
                        value={editingCategory.nome}
                        onChange={(event) => setEditingCategory((current) => ({ ...current, nome: event.target.value }))}
                      />
                      <input
                        value={editingCategory.descricao}
                        onChange={(event) => setEditingCategory((current) => ({ ...current, descricao: event.target.value }))}
                      />
                    </>
                  ) : (
                    <>
                      <strong>{categoria.nome}</strong>
                      <span>{categoria.descricao || "Sem descricao"}</span>
                    </>
                  )}
                </div>
                <div className="category-meta">
                  <span>{serviceCountByCategory[categoria.id] || 0} servicos</span>
                  <StatusBadge value={categoria.ativo ? "ativo" : "inativo"} />
                </div>
                <div className="table-actions">
                  {editing ? (
                    <>
                      <button className="small-button" onClick={() => saveCategoryEdit(categoria)}>Salvar</button>
                      <button className="small-button neutral" onClick={() => setEditingCategoryId(null)}>Cancelar</button>
                    </>
                  ) : (
                    <>
                      <button
                        className="small-button"
                        onClick={() => {
                          setEditingCategoryId(categoria.id);
                          setEditingCategory({ nome: categoria.nome, descricao: categoria.descricao || "" });
                        }}
                      >
                        Editar
                      </button>
                      <button className="small-button danger" onClick={() => toggleCategory(categoria)}>
                        {categoria.ativo ? "Desativar" : "Ativar"}
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </article>

      <article className="panel">
        <div className="card-heading">
          <div>
            <h2>Servicos cadastrados</h2>
            <p>Descricao completa fica no editar. Aqui aparece apenas o resumo para manter a tabela limpa.</p>
          </div>
        </div>
        {loading ? <LoadingBlock message="Carregando servicos..." /> : (
          <DataTable
            rows={servicos}
            columns={[
              { key: "nome", label: "Servico", render: (row) => <strong>{row.nome}</strong> },
              { key: "categoria_id", label: "Categoria", render: (row) => categoryName(row.categoria_id, categorias) },
              { key: "preco_mao_obra", label: "Preco", render: (row) => money(row.preco_mao_obra) },
              { key: "tempo_estimado_minutos", label: "Tempo", render: (row) => `${row.tempo_estimado_minutos} min` },
              { key: "precisa_material", label: "Material", render: (row) => row.precisa_material ? "Sim" : "Nao" },
              { key: "ativo", label: "Status", render: (row) => <StatusBadge value={row.ativo ? "ativo" : "inativo"} /> },
              {
                key: "actions",
                label: "Acoes",
                render: (row) => (
                  <div className="table-actions">
                    <button className="small-button" onClick={() => startEdit(row)}>Editar</button>
                    <button className="small-button neutral" onClick={() => startEdit(row)}>Ver detalhes</button>
                    <button className="small-button danger" onClick={() => toggleService(row)}>
                      {row.ativo ? "Desativar" : "Ativar"}
                    </button>
                  </div>
                ),
              },
            ]}
          />
        )}
      </article>
    </section>
  );
}

function validateServicoForm(form) {
  const errors = {};
  const preco = Number(form.preco_mao_obra);
  const minimo = Number(form.tempo_minimo);
  const maximo = Number(form.tempo_maximo);
  if (!form.categoria_id) errors.categoria_id = "Escolha uma categoria.";
  if (!form.nome.trim()) errors.nome = "Informe o nome do servico.";
  if (form.preco_mao_obra === "" || Number.isNaN(preco) || preco < 0) {
    errors.preco_mao_obra = "Informe um preco valido.";
  }
  if (form.tempo_minimo === "" || Number.isNaN(minimo) || minimo <= 0) {
    errors.tempo_minimo = "Informe o tempo minimo.";
  }
  if (form.tempo_maximo === "" || Number.isNaN(maximo) || maximo <= 0) {
    errors.tempo_maximo = "Informe o tempo maximo.";
  }
  if (!errors.tempo_minimo && !errors.tempo_maximo && minimo > maximo) {
    errors.tempo_maximo = "Tempo maximo nao pode ser menor que o minimo.";
  }
  if (!form.descricao.trim()) {
    errors.descricao = "Informe a descricao para o cliente.";
  } else if (form.descricao.trim().length < 10) {
    errors.descricao = "Use pelo menos 10 caracteres.";
  }
  return errors;
}

function buildDescription(form) {
  const pieces = [form.descricao.trim()];
  if (form.material_padrao.trim()) {
    pieces.push(`Material comum: ${form.material_padrao.trim()}`);
  }
  if (form.observacao_interna.trim()) {
    pieces.push(`Observacao interna: ${form.observacao_interna.trim()}`);
  }
  return pieces.join("\n\n");
}

function toMinutes(value, unit) {
  if (unit === "horas") return value * 60;
  if (unit === "dias") return value * 24 * 60;
  return value;
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
