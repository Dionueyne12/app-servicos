import { useEffect, useState } from "react";

import { getDashboard, getFinanceiro, getMonitoramento, listPrestadoresPendentes } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import MetricCard from "../components/MetricCard.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date, money, statusLabel } from "../utils/format.js";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [financeiro, setFinanceiro] = useState(null);
  const [monitoramento, setMonitoramento] = useState(null);
  const [pendentes, setPendentes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [dashboard, fin, mon, prestadoresPendentes] = await Promise.all([
        getDashboard(),
        getFinanceiro(),
        getMonitoramento(),
        listPrestadoresPendentes({ per_page: 1 }),
      ]);
      setData(dashboard);
      setFinanceiro(fin);
      setMonitoramento(mon);
      setPendentes(prestadoresPendentes?.meta?.total || 0);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingBlock message="Carregando dashboard..." />;

  return (
    <section>
      <Toolbar title="Dashboard" description="Visao geral para acompanhar saude, operacao e dinheiro do app.">
        <button className="ghost-button" onClick={load}>Atualizar</button>
      </Toolbar>
      <ErrorBlock message={error} onRetry={load} />
      <div className="metric-grid">
        <MetricCard title="Clientes" value={data?.total_clientes || 0} />
        <MetricCard title="Prestadores" value={data?.total_prestadores || 0} />
        <MetricCard title="Prestadores pendentes" value={pendentes} tone="orange" />
        <MetricCard title="Abertas" value={data?.solicitacoes_aguardando_prestador || 0} tone="orange" />
        <MetricCard title="Em andamento" value={data?.solicitacoes_em_andamento || 0} tone="green" />
        <MetricCard title="Concluidas" value={data?.solicitacoes_concluidas || 0} tone="green" />
        <MetricCard title="Em analise" value={data?.solicitacoes_em_analise || 0} tone="red" />
        <MetricCard title="Faturamento simulado" value={money(financeiro?.valor_total_estimado || data?.valor_total_estimado)} />
        <MetricCard title="Comissao plataforma" value={money(financeiro?.valor_total_comissao_plataforma)} />
        <MetricCard title="Repasses pendentes" value={money(financeiro?.repasses_pendentes?.valor_total)} tone="orange" />
        <MetricCard title="Alertas criticos" value={monitoramento?.por_nivel?.critico || 0} tone="red" />
      </div>

      <div className="panel-grid">
        <article className="panel">
          <h2>Ultimas solicitacoes</h2>
          <DataTable
            rows={data?.ultimos_servicos_criados || []}
            columns={[
              { key: "descricao", label: "Servico" },
              { key: "status", label: "Status", render: (row) => <StatusBadge value={row.status} /> },
              { key: "valor_total_estimado", label: "Valor", render: (row) => money(row.valor_total_estimado) },
              { key: "created_at", label: "Data", render: (row) => date(row.created_at) },
            ]}
          />
        </article>
        <article className="panel">
          <h2>Ultimos usuarios</h2>
          <DataTable
            rows={data?.ultimos_usuarios_cadastrados || []}
            columns={[
              { key: "nome", label: "Nome" },
              { key: "tipo_usuario", label: "Perfil", render: (row) => statusLabel(row.tipo_usuario) },
              { key: "email", label: "E-mail" },
              { key: "created_at", label: "Cadastro", render: (row) => date(row.created_at) },
            ]}
          />
        </article>
      </div>

      <article className="panel">
        <h2>Alertas recentes do monitoramento</h2>
        <DataTable
          rows={monitoramento?.alertas_ativos?.slice(0, 8) || []}
          columns={[
            { key: "nivel_alerta", label: "Nivel", render: (row) => <StatusBadge value={row.nivel_alerta} /> },
            { key: "tipo_alerta", label: "Tipo", render: (row) => statusLabel(row.tipo_alerta) },
            { key: "mensagem", label: "Mensagem" },
            { key: "created_at", label: "Data", render: (row) => date(row.created_at) },
          ]}
        />
      </article>
    </section>
  );
}
