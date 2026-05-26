import { useEffect, useState } from "react";

import { getFinanceiro, listRepasses } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import MetricCard from "../components/MetricCard.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date, money } from "../utils/format.js";

export default function FinanceiroPage() {
  const [financeiro, setFinanceiro] = useState(null);
  const [repasses, setRepasses] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [fin, reps] = await Promise.all([getFinanceiro(), listRepasses({ per_page: 50 })]);
      setFinanceiro(fin);
      setRepasses(reps);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingBlock message="Carregando financeiro..." />;

  return (
    <section>
      <Toolbar title="Financeiro" description="Separe plataforma, prestador e fornecedor com clareza." />
      <ErrorBlock message={error} onRetry={load} />
      <div className="metric-grid">
        <MetricCard title="Pagamentos" value={financeiro?.total_pagamentos || 0} />
        <MetricCard title="Mao de obra" value={money(financeiro?.valor_total_mao_obra)} />
        <MetricCard title="Material" value={money(financeiro?.valor_total_materiais)} />
        <MetricCard title="Total estimado" value={money(financeiro?.valor_total_estimado)} />
        <MetricCard title="Comissao plataforma" value={money(financeiro?.valor_total_comissao_plataforma)} tone="green" />
        <MetricCard title="A pagar prestadores" value={money(financeiro?.valor_total_prestadores)} tone="orange" />
        <MetricCard title="A pagar fornecedores" value={money(financeiro?.valor_total_empresas)} tone="orange" />
        <MetricCard title="Ticket medio" value={money(financeiro?.ticket_medio)} />
      </div>
      <article className="panel">
        <h2>Repasses</h2>
        <DataTable
          rows={repasses.items || []}
          columns={[
            { key: "tipo_repasse", label: "Tipo" },
            { key: "status_repasse", label: "Status", render: (row) => <StatusBadge value={row.status_repasse} /> },
            { key: "valor", label: "Valor", render: (row) => money(row.valor) },
            { key: "created_at", label: "Data", render: (row) => date(row.created_at) },
          ]}
        />
      </article>
    </section>
  );
}
