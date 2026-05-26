import { useEffect, useState } from "react";

import { listSolicitacoes } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date, money } from "../utils/format.js";

export default function SolicitacoesPage() {
  const [filters, setFilters] = useState({ status: "", cliente_id: "", prestador_id: "", categoria: "" });
  const [data, setData] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await listSolicitacoes({ per_page: 50, ...clean(filters) }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section>
      <Toolbar title="Solicitacoes" description="Acompanhe status, valores, materiais e proximos passos." />
      <div className="panel filter-grid">
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">Todos os status</option>
          {["aguardando_prestador", "aceito", "aguardando_aprovacao_cliente", "em_andamento", "concluido", "cancelado", "em_analise"].map((status) => (
            <option key={status} value={status}>{status.replaceAll("_", " ")}</option>
          ))}
        </select>
        <input placeholder="Cliente ID" value={filters.cliente_id} onChange={(e) => setFilters({ ...filters, cliente_id: e.target.value })} />
        <input placeholder="Prestador ID" value={filters.prestador_id} onChange={(e) => setFilters({ ...filters, prestador_id: e.target.value })} />
        <input placeholder="Categoria" value={filters.categoria} onChange={(e) => setFilters({ ...filters, categoria: e.target.value })} />
        <button onClick={load}>Filtrar</button>
      </div>
      <ErrorBlock message={error} onRetry={load} />
      {loading ? <LoadingBlock message="Carregando solicitacoes..." /> : (
        <DataTable
          rows={data.items || []}
          columns={[
            { key: "descricao", label: "Servico" },
            { key: "cliente_id", label: "Cliente" },
            { key: "prestador_id", label: "Prestador" },
            { key: "valor_mao_obra", label: "Mao de obra", render: (row) => money(row.valor_mao_obra) },
            { key: "valor_material", label: "Material", render: (row) => money(row.valor_material) },
            { key: "valor_total_estimado", label: "Total", render: (row) => money(row.valor_total_estimado) },
            { key: "status", label: "Status", render: (row) => <StatusBadge value={row.status} /> },
            { key: "created_at", label: "Data", render: (row) => date(row.created_at) },
            { key: "actions", label: "Acoes", render: () => <button>Ver detalhes</button> },
          ]}
        />
      )}
    </section>
  );
}

function clean(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value));
}
