import { API_BASE_URL } from "../api/client.js";
import Toolbar from "../components/Toolbar.jsx";

export default function ConfiguracoesPage() {
  return (
    <section>
      <Toolbar title="Configuracoes" description="Informacoes tecnicas simples para operacao do painel." />
      <article className="panel">
        <h2>API conectada</h2>
        <p className="code-line">{API_BASE_URL || "VITE_API_BASE_URL nao configurada"}</p>
        <p>
          Para hospedagem online, configure esta variavel no provedor do painel.
          Nao existe URL localhost fixa no codigo.
        </p>
      </article>
    </section>
  );
}
