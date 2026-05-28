import { useEffect, useState } from "react";

import { listClientes } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage } from "../utils/format.js";

export default function ClientesPage() {
  const [data, setData] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await listClientes({ per_page: 50 }));
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
      <Toolbar title="Clientes" description="Veja clientes, contato, endereco resumido e historico." />
      <ErrorBlock message={error} onRetry={load} />
      <article className="panel">
        <div className="card-heading">
          <div>
            <h2>Clientes cadastrados</h2>
            <p>Dados resumidos para leitura rapida. Detalhes completos ficam no historico.</p>
          </div>
        </div>
        {loading ? <LoadingBlock message="Carregando clientes..." /> : (
          <DataTable
            rows={data.items || []}
            columns={[
              {
                key: "cliente",
                label: "Cliente",
                render: (row) => (
                  <div className="person-cell">
                    <strong>{row.nome || "-"}</strong>
                    <span>{row.email || "-"}</span>
                  </div>
                ),
              },
              { key: "telefone", label: "Contato", render: (row) => row.telefone || "-" },
              { key: "endereco", label: "Endereco", render: (row) => shortAddress(row) },
              { key: "total_servicos_solicitados", label: "Solicitacoes", render: (row) => row.total_servicos_solicitados || 0 },
              { key: "media_notas", label: "Avaliacao", render: (row) => Number(row.media_notas || 0).toFixed(1) },
              { key: "created_at", label: "Cadastro", render: (row) => formatDateTime(row.created_at) },
              {
                key: "actions",
                label: "Acoes",
                render: () => (
                  <div className="table-actions">
                    <button className="small-button neutral">Ver historico</button>
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

function shortAddress(row) {
  const area = row.bairro || row.endereco;
  const city = row.cidade;
  return [area, city].filter(Boolean).join(", ") || "-";
}

function formatDateTime(value) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "-";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsed).replace(",", " as");
}
