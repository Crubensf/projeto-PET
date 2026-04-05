import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import logoPet from "../assets/logopet.png";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function handleSubmit(e) {
  e.preventDefault();
  setErr("");
  setLoading(true);

  try {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", senha);

    const res = await fetch(`${import.meta.env.VITE_API_BASE}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data?.detail || "Falha no login");
    }

    const token = data.access_token;

    localStorage.setItem("access_token", token);

    navigate("/", { replace: true });

  } catch (e) {
    setErr(e.message);
  } finally {
    setLoading(false);
  }
}
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.brand}>
          <img src={logoPet} alt="PET Saúde" style={styles.logo} />
          <div>
            <div style={styles.brandTitle}>PET Saúde</div>
            <div style={styles.brandSub}>Agendamento UBS</div>
          </div>
        </div>

        <h1 style={styles.h1}>Entrar</h1>
        <p style={styles.h2}>Use seu e-mail e senha para acessar o sistema.</p>

        {err ? <div style={styles.alertErr}>{err}</div> : null}

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.field}>
            <span style={styles.label}>E-mail</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              required
              autoComplete="email"
            />
          </label>

          <label style={styles.field}>
            <span style={styles.label}>Senha</span>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              style={styles.input}
              required
              autoComplete="current-password"
            />
          </label>

          <button type="submit" disabled={loading} style={styles.primaryBtn}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <div style={styles.footer}>
          <span style={styles.footerText}>Ainda não tem acesso?</span>
          <Link to="/cadastro-usuario" style={styles.footerLink}>
            Cadastrar usuário
          </Link>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "grid",
    placeItems: "center",
    background: "#f3f8ff",
    padding: 16,
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
  },
  card: {
    width: "100%",
    maxWidth: 420,
    background: "white",
    borderRadius: 20,
    border: "1px solid #dbeafe",
    boxShadow: "0 16px 40px rgba(15,23,42,0.12)",
    padding: 20,
    boxSizing: "border-box",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 10,
  },
  logo: { width: 48, height: 48, objectFit: "contain" },
  brandTitle: { fontSize: 14, fontWeight: 900, color: "#0f172a" },
  brandSub: { fontSize: 12, color: "#64748b" },

  h1: { fontSize: 20, fontWeight: 900, marginTop: 8, marginBottom: 4 },
  h2: { fontSize: 13, color: "#475569", marginBottom: 12 },

  alertErr: {
    padding: 10,
    borderRadius: 12,
    border: "1px solid #fecaca",
    background: "#fff1f2",
    color: "#991b1b",
    fontSize: 13,
    marginBottom: 10,
  },

  form: { display: "grid", gap: 10, marginTop: 4 },
  field: { display: "grid", gap: 6 },
  label: { fontSize: 12, fontWeight: 800, color: "#334155" },
  input: {
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    outline: "none",
    fontSize: 14,
  },
  primaryBtn: {
    marginTop: 4,
    padding: "10px 14px",
    borderRadius: 12,
    border: "1px solid #1d4ed8",
    background: "#1d4ed8",
    color: "white",
    fontWeight: 900,
    cursor: "pointer",
  },

  footer: {
    marginTop: 14,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontSize: 12,
  },
  footerText: { color: "#64748b" },
  footerLink: { color: "#1d4ed8", fontWeight: 800, textDecoration: "none" },
};
