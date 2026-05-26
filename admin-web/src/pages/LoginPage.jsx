import { useState } from "react";

import { useAuth } from "../context/AuthContext.jsx";
import { apiErrorMessage } from "../utils/format.js";

export default function LoginPage() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (!email.trim() || !senha) {
      setError("Informe e-mail e senha para entrar.");
      return;
    }
    setLoading(true);
    try {
      await signIn(email, senha);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="brand center">
          <div className="brand-mark">AS</div>
          <div>
            <strong>Painel Admin</strong>
            <span>Entre para controlar a plataforma</span>
          </div>
        </div>
        <form onSubmit={handleSubmit}>
          <label>
            E-mail
            <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="admin@email.com" />
          </label>
          <label>
            Senha
            <div className="password-row">
              <input
                value={senha}
                onChange={(event) => setSenha(event.target.value)}
                type={showPassword ? "text" : "password"}
                placeholder="Sua senha"
              />
              <button type="button" onClick={() => setShowPassword((current) => !current)}>
                {showPassword ? "Ocultar" : "Ver"}
              </button>
            </div>
          </label>
          {error ? <div className="form-error">{error}</div> : null}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}
