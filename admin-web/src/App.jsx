import { useState } from "react";

import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import PrestadoresPage from "./pages/PrestadoresPage.jsx";
import ClientesPage from "./pages/ClientesPage.jsx";
import ServicosPage from "./pages/ServicosPage.jsx";
import SolicitacoesPage from "./pages/SolicitacoesPage.jsx";
import FinanceiroPage from "./pages/FinanceiroPage.jsx";
import WarrantyPage from "./pages/WarrantyPage.jsx";
import FornecedoresPage from "./pages/FornecedoresPage.jsx";
import MonitoramentoPage from "./pages/MonitoramentoPage.jsx";
import ConfiguracoesPage from "./pages/ConfiguracoesPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import { LoadingBlock } from "./components/StateBlock.jsx";

const pages = {
  dashboard: DashboardPage,
  prestadores: PrestadoresPage,
  clientes: ClientesPage,
  servicos: ServicosPage,
  solicitacoes: SolicitacoesPage,
  financeiro: FinanceiroPage,
  garantias: WarrantyPage,
  fornecedores: FornecedoresPage,
  monitoramento: MonitoramentoPage,
  configuracoes: ConfiguracoesPage,
};

const menu = [
  ["dashboard", "Dashboard", "DB"],
  ["prestadores", "Prestadores", "PR"],
  ["clientes", "Clientes", "CL"],
  ["servicos", "Servicos", "SV"],
  ["solicitacoes", "Solicitacoes", "SO"],
  ["financeiro", "Financeiro", "FI"],
  ["garantias", "Garantias", "GA"],
  ["fornecedores", "Fornecedores", "FO"],
  ["monitoramento", "Monitoramento", "MO"],
  ["configuracoes", "Configuracoes", "CF"],
];

export default function App() {
  return (
    <AuthProvider>
      <AdminApp />
    </AuthProvider>
  );
}

function AdminApp() {
  const { isAuthenticated, loading } = useAuth();
  const [active, setActive] = useState("dashboard");

  if (loading) {
    return (
      <main className="login-shell">
        <LoadingBlock message="Preparando painel..." />
      </main>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const Page = pages[active] || DashboardPage;
  return (
    <div className="admin-shell">
      <Sidebar active={active} onChange={setActive} />
      <main className="content-shell">
        <Topbar />
        <Page />
      </main>
    </div>
  );
}

function Sidebar({ active, onChange }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">AS</div>
        <div>
          <strong>App Servicos</strong>
          <span>Painel do dono</span>
        </div>
      </div>
      <nav>
        {menu.map(([key, label, icon]) => (
          <button
            key={key}
            type="button"
            className={active === key ? "nav-item active" : "nav-item"}
            onClick={() => onChange(key)}
          >
            <span>{icon}</span>
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}

function Topbar() {
  const { user, logout } = useAuth();
  return (
    <header className="topbar">
      <div>
        <strong>{user?.nome || "Administrador"}</strong>
        <span>Controle operacional da plataforma</span>
      </div>
      <button type="button" className="danger-button" onClick={logout}>Sair</button>
    </header>
  );
}
