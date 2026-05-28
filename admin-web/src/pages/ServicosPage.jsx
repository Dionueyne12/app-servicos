import { useEffect, useState } from "react";

import {
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

export default function ServicosPage() {
  const [data, setData] = useState({ items: [] });
  const [categorias, setCategorias] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
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

  function startEdit(row) {
    setError("");
    setFieldErrors({});
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

  return (
    <section>
      <Toolbar title="Servicos tabelados" description="Controle nomes, precos e tempo estimado sem alterar codigo." />
      <ErrorBlock message={error} onRetry={load} />
      <form className="panel form-grid" onSubmit={save}>
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
        </label>
        <label className="field-group">
          <span>Nome do servico</span>
          <input
            className={fieldErrors.nome ? "input-error" : ""}
            placeholder="Ex: Trocar chuveiro"
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
            placeholder="Explique o que esta incluido no servico."
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
          Possui garantia
        </label>
        {form.possui_garantia ? (
          <>
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
          </>
        ) : null}
        <button className="primary-button" disabled={saving}>{saving ? "Salvando..." : form.id ? "Salvar alteracoes" : "Criar servico"}</button>
        {form.id ? (
          <button type="button" className="ghost-button" onClick={() => { setForm(emptyForm); setFieldErrors({}); }}>
            Cancelar edicao
          </button>
        ) : null}
      </form>
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
