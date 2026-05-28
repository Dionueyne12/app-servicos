import { useEffect, useState } from "react";

import {
  bloquearRetencaoGarantia,
  liberarRetencaoGarantia,
  listGarantias,
  negarGarantia,
  resolverGarantia,
} from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date, money } from "../utils/format.js";

export default function GarantiasPage() {
  const [status, setStatus] = useState("");
  const [data, setData] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setData(await listGarantias({ per_page: 50, ...(status ? { status_garantia: status } : {}) }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function runAction(action, row) {
    const observacao = window.prompt("Observacao para historico administrativo:", "") || "";
    setError("");
    try {
      await action(row.id, observacao);
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  return (
    <section>
      <Toolbar title="Garantias" description="Acompanhe garantias, retencoes e analises antes de liberar repasses." />
      <div className="panel filter-grid">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">Todas as garantias</option>
          {["ativa", "expirada", "acionada", "em_analise", "resolvida", "negada"].map((item) => (
            <option key={item} value={item}>{item.replaceAll("_", " ")}</option>
          ))}
        </select>
        <button onClick={load}>Filtrar</button>
      </div>
      <ErrorBlock message={error} onRetry={load} />
      {loading ? <LoadingBlock message="Carregando garantias..." /> : (
        <DataTable
          rows={data.items || []}
          columns={[
            { key: "solicitacao_id", label: "Solicitacao" },
            { key: "prestador_id", label: "Prestador" },
            { key: "status_garantia", label: "Status", render: (row) => <StatusBadge value={row.status_garantia} /> },
            { key: "valor_retido", label: "Retido", render: (row) => money(row.valor_retido) },
            { key: "valor_liberado_inicial", label: "Liberado inicial", render: (row) => money(row.valor_liberado_inicial) },
            { key: "data_fim_garantia", label: "Fim garantia", render: (row) => date(row.data_fim_garantia) },
            {
              key: "bloqueio_repasse",
              label: "Repasse",
              render: (row) => row.bloqueio_repasse ? <StatusBadge value="bloqueado" /> : <StatusBadge value="liberavel" />,
            },
            {
              key: "actions",
              label: "Acoes",
              render: (row) => (
                <div className="row-actions">
                  <button onClick={() => runAction(bloquearRetencaoGarantia, row)}>Bloquear</button>
                  <button onClick={() => runAction(liberarRetencaoGarantia, row)}>Liberar</button>
                  <button onClick={() => runAction(resolverGarantia, row)}>Resolver</button>
                  <button className="danger-link" onClick={() => runAction(negarGarantia, row)}>Negar</button>
                </div>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}
