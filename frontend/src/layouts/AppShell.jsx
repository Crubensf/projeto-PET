import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import logoPet from "../assets/logopet.png";

export default function AppShell() {
  const navigate = useNavigate();

  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  function handleLogout() {
    localStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  }

  return (
    <div style={styles.page}>
      <header style={styles.topbar}>
        <div style={styles.topbarInner}>
          <div
            style={styles.brand}
            role="button"
            tabIndex={0}
            onClick={() => navigate("/dashboard")}
          >
            <img src={logoPet} alt="PET Saúde" style={styles.logoImg} />
            <div>
              <div style={styles.brandTitle}>PET Saúde</div>
              <div style={styles.brandSub}>Agendamento UBS</div>
            </div>
          </div>

          <div style={styles.rightSide}>
            <nav style={styles.nav}>
              <NavItem to="/dashboard">Dashboard</NavItem>
              <NavItem to="/agendamento">Agendar</NavItem>
              <NavItem to="/agendamentos-crud">Gerenciar agendamentos</NavItem>
              <NavItem to="/pacientes">Pacientes</NavItem>
              <NavItem to="/profissionais">Profissionais</NavItem>
            </nav>

            {token ? (
              <button
                type="button"
                style={styles.logoutBtn}
                onClick={handleLogout}
              >
                Sair
              </button>
            ) : null}
          </div>
        </div>
      </header>

      <main style={styles.container}>
        <Outlet />
      </main>
    </div>
  );
}

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      style={({ isActive }) =>
        isActive
          ? { ...styles.navBtn, ...styles.navBtnActive }
          : styles.navBtn
      }
    >
      {children}
    </NavLink>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f3f8ff",
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
  },
  topbar: {
    background: "white",
    borderBottom: "1px solid #dbeafe",
    position: "sticky",
    top: 0,
    zIndex: 20,
  },
  topbarInner: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "12px 16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    flexWrap: "wrap",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: 14,
    cursor: "pointer",
  },
  logoImg: {
    width: 56,
    height: 56,
    objectFit: "contain",
  },
  brandTitle: { fontSize: 14, fontWeight: 900, color: "#0f172a" },
  brandSub: { fontSize: 12, color: "#334155", marginTop: 2 },

  rightSide: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    flexWrap: "wrap",
  },

  nav: { display: "flex", gap: 8, flexWrap: "wrap" },
  navBtn: {
    padding: "8px 10px",
    borderRadius: 12,
    border: "1px solid #dbeafe",
    background: "#eff6ff",
    color: "#0f172a",
    fontWeight: 800,
    cursor: "pointer",
    textDecoration: "none",
    fontSize: 13,
  },
  navBtnActive: {
    background: "#1d4ed8",
    borderColor: "#1d4ed8",
    color: "white",
  },

  logoutBtn: {
    padding: "8px 10px",
    borderRadius: 12,
    border: "1px solid #fecaca",
    background: "#fff1f2",
    color: "#991b1b",
    fontWeight: 800,
    cursor: "pointer",
    fontSize: 13,
  },

  container: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "16px 16px 28px",
  },
};
