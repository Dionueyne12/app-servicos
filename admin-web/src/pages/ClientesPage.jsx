import { useEffect, useState } from "react";

import { listClientes } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date } from "../utils/format.js";

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
      <Toolbar title="Clientes" description="Historico, reputacao e sinais de comportamento dos clientes." />
      <ErrorBlock message={error} onRetry={load} />
      {loading ? <LoadingBlock message="Carregando clientes..." /> : (
        <DataTable
          rows={data.items || []}
          columns={[
            { key: "nome", label: "Nome" },
            { key: "email", label: "E-mail" },
            { key: "telefone", label: "Telefone" },
            { key: "endereco", label: "Endereco", render: (row) => `${row.endereco || "-"} ${row.bairro ? `/ ${row.bairro}` : ""} ${row.cidade ? `/ ${row.cidade}` : ""}` },
            { key: "total_servicos_solicitados", label: "Solicitacoes" },
            { key: "media_notas", label: "Avaliacao", render: (row) => Number(row.media_notas || 0).toFixed(1) },
            { key: "created_at", label: "Cadastro", render: (row) => date(row.created_at) },
            { key: "actions", label: "Acoes", render: () => <button>Ver historico</button> },
          ]}
        />
      )}
    </section>
  );
}
