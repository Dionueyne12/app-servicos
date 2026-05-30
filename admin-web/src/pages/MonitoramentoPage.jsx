import { useEffect, useState } from "react";

import { getMonitoramento } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import MetricCard from "../components/MetricCard.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date, statusLabel } from "../utils/format.js";

export default function MonitoramentoPage() {
  const [data, setData] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const monitoramento = await getMonitoramento();
      setData(monitoramento);
      setSelectedAlert(null);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingBlock message="Carregando monitoramento..." />;

  const selectedAnalysis = selectedAlert?.analise_portugues_simples || data?.analise_portugues_simples;

  return (
    <section>
      <div className="version-marker">VERSAO IA AUXILIAR V1</div>
      <Toolbar title="Monitoramento" description="Sinais preventivos antes do sistema virar problema.">
        <button className="ghost-button" onClick={load}>Atualizar</button>
      </Toolbar>
      <ErrorBlock message={error} onRetry={load} />
      <div className="metric-grid">
        <MetricCard title="Saude do sistema" value={statusLabel(data?.saude)} tone={data?.saude === "ok" ? "green" : "orange"} />
        <MetricCard title="Criticos" value={data?.por_nivel?.critico || 0} tone="red" />
        <MetricCard title="Alertas" value={data?.por_nivel?.alerta || 0} tone="orange" />
        <MetricCard title="Ativos" value={data?.alertas_ativos?.length || 0} />
      </div>
      <article className="panel">
        <h2>Alertas ativos</h2>
        <DataTable
          rows={data?.alertas_ativos || []}
          onRowClick={setSelectedAlert}
          selectedRowId={selectedAlert?.id}
          columns={[
            { key: "nivel_alerta", label: "Nivel", render: (row) => <StatusBadge value={row.nivel_alerta} /> },
            { key: "tipo_alerta", label: "Tipo", render: (row) => statusLabel(row.tipo_alerta) },
            { key: "origem", label: "Origem" },
            { key: "mensagem", label: "Mensagem" },
            { key: "created_at", label: "Data", render: (row) => date(row.created_at) },
          ]}
        />
      </article>
      {selectedAlert ? (
        <article className="panel alert-detail-panel">
          <div className="card-heading">
            <div>
              <h2>Analise em portugues simples</h2>
              <p>{statusLabel(selectedAlert.tipo_alerta)} - {selectedAlert.origem}</p>
            </div>
            <StatusBadge value={selectedAlert.nivel_alerta} />
          </div>
          <div className="analysis-grid detail-analysis-grid">
            <div>
              <span>O que aconteceu</span>
              <strong>{selectedAnalysis?.explicacao_simples || "-"}</strong>
            </div>
            <div>
              <span>Provavel causa</span>
              <strong>{selectedAnalysis?.provavel_causa || "-"}</strong>
            </div>
            <div>
              <span>Gravidade sugerida</span>
              <strong>{statusLabel(selectedAnalysis?.gravidade_sugerida) || "-"}</strong>
            </div>
            <div>
              <span>Acao recomendada</span>
              <strong>{selectedAnalysis?.acao_recomendada || "-"}</strong>
            </div>
          </div>
        </article>
      ) : null}
      <div className="panel-grid">
        <article className="panel">
          <h2>Rotas mais lentas</h2>
          <DataTable
            rows={data?.rotas_mais_lentas || []}
            columns={[
              { key: "tipo_alerta", label: "Tipo", render: (row) => statusLabel(row.tipo_alerta) },
              { key: "mensagem", label: "Mensagem" },
            ]}
          />
        </article>
        <article className="panel">
          <h2>Problemas futuros</h2>
          <ul className="simple-list">
            {(data?.possiveis_problemas_futuros || []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </article>
      </div>
    </section>
  );
}
