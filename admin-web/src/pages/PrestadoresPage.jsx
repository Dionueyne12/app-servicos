import { useEffect, useMemo, useState } from "react";

import { approvePrestador, getPrestadorDocs, listPrestadores, listPrestadoresPendentes, rejectPrestador } from "../api/admin.js";
import DataTable from "../components/DataTable.jsx";
import { ErrorBlock, LoadingBlock } from "../components/StateBlock.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import Toolbar from "../components/Toolbar.jsx";
import { apiErrorMessage, date } from "../utils/format.js";

export default function PrestadoresPage() {
  const [tab, setTab] = useState("pendentes");
  const [data, setData] = useState({ items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const title = useMemo(() => ({ pendentes: "Pendentes", aprovados: "Aprovados", rejeitados: "Rejeitados" })[tab], [tab]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      if (tab === "pendentes") {
        setData(await listPrestadoresPendentes({ per_page: 50 }));
      } else {
        setData(await listPrestadores({
          per_page: 50,
          status_validacao: tab === "aprovados" ? "aprovado" : "rejeitado",
        }));
      }
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tab]);

  async function approve(id) {
    await approvePrestador(id);
    load();
  }

  async function reject(id) {
    const observacao = window.prompt("Informe o motivo da rejeicao:");
    if (!observacao) return;
    await rejectPrestador(id, observacao);
    load();
  }

  async function docs(id) {
    try {
      const details = await getPrestadorDocs(id);
      window.alert(JSON.stringify(details, null, 2));
    } catch (err) {
      window.alert(apiErrorMessage(err));
    }
  }

  return (
    <section>
      <Toolbar title="Prestadores" description="Aprove, rejeite e acompanhe quem atende pela plataforma.">
        <button className="ghost-button" onClick={load}>Atualizar</button>
      </Toolbar>
      <div className="tabs">
        {["pendentes", "aprovados", "rejeitados"].map((item) => (
          <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)}>{item}</button>
        ))}
      </div>
      <ErrorBlock message={error} onRetry={load} />
      {loading ? <LoadingBlock message={`Carregando prestadores ${title.toLowerCase()}...`} /> : (
        <DataTable
          rows={data.items || []}
          columns={[
            { key: "nome", label: "Nome" },
            { key: "email", label: "E-mail" },
            { key: "telefone", label: "Telefone" },
            { key: "cidade", label: "Cidade/Bairro", render: (row) => `${row.cidade || "-"} ${row.bairro ? `/ ${row.bairro}` : ""}` },
            { key: "documento", label: "Documento" },
            { key: "status_validacao", label: "Status", render: (row) => <StatusBadge value={row.status_validacao || (row.ativo ? "aprovado" : "rejeitado")} /> },
            { key: "media_notas", label: "Nota", render: (row) => Number(row.media_notas || 0).toFixed(1) },
            { key: "total_servicos_concluidos", label: "Servicos" },
            { key: "created_at", label: "Cadastro", render: (row) => date(row.created_at) },
            {
              key: "actions",
              label: "Acoes",
              render: (row) => (
                <div className="row-actions">
                  <button onClick={() => docs(row.id)}>Detalhes</button>
                  {tab === "pendentes" ? <button onClick={() => approve(row.id)}>Aprovar</button> : null}
                  {tab !== "rejeitados" ? <button className="danger-link" onClick={() => reject(row.id)}>Rejeitar</button> : null}
                </div>
              ),
            },
          ]}
        />
      )}
    </section>
  );
}
