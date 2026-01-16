import React, { useCallback, useEffect, useMemo, useState } from "react";
import { dashboardService } from "../services/dashboardService";

function formatBRDateTime(iso) {
  return new Date(iso).toLocaleString("pt-BR");
}

function todayISO() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

function minusDaysISO(days) {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [resumo, setResumo] = useState(null);
  const [proximos, setProximos] = useState([]);
  const [serie, setSerie] = useState([]);
  const [ranking, setRanking] = useState([]);

  const range = useMemo(
    () => ({ start: minusDaysISO(6), end: todayISO() }),
    []
  );

  const load = useCallback(async () => {
    setLoading(true);
    setErr("");
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        dashboardService.resumo(),
        dashboardService.proximos(10),
        dashboardService.porDia(range),
        dashboardService.porEspecialidade({
          start: minusDaysISO(29),
          end: todayISO(),
          limit: 10,
        }),
      ]);

      setResumo(r1);
      setProximos(r2);
      setSerie(r3);
      setRanking(r4);
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <div style={styles.header}>
        <div>
          <div style={styles.h1}>Dashboard</div>
          <div style={styles.h2}>
            Visão geral do sistema de agendamento
          </div>
        </div>

        <button onClick={load} disabled={loading} style={styles.primaryBtn}>
          {loading ? "Atualizando..." : "Atualizar"}
        </button>
      </div>

      {err ? <div style={styles.alertErr}>{err}</div> : null}

      <div style={styles.kpiGrid}>
        <Kpi label="Pacientes" value={resumo?.total_pacientes} />
        <Kpi label="Profissionais" value={resumo?.total_profissionais} />
        <Kpi label="Especialidades" value={resumo?.total_especialidades} />
        <Kpi label="Locais" value={resumo?.total_locais} />
        <Kpi label="Agendamentos" value={resumo?.total_agendamentos} />
        <Kpi label="Hoje" value={resumo?.agendamentos_hoje} />
      </div>

      <Section title="Próximos agendamentos">
        <Table
          cols={[
            "Início",
            "Paciente",
            "Especialidade",
            "Profissional",
            "CRM",
            "Local",
            "Modalidade",
            "Agendado por",
          ]}
          rows={
            loading
              ? []
              : proximos.map((a) => {
                  const crm =
                    a.profissional_crm && a.profissional_crm_uf
                      ? `${a.profissional_crm}-${a.profissional_crm_uf}`
                      : a.profissional_crm || "—";

                  return [
                    formatBRDateTime(a.inicio),
                    a.paciente_nome,
                    a.especialidade_nome,
                    a.profissional_nome,
                    crm,
                    a.local_nome,
                    a.modalidade,
                    a.criado_por_nome || "—",
                  ];
                })
          }
          empty="Nenhum agendamento futuro."
        />
      </Section>

      <div style={styles.twoCols}>
        <Section title={`Agendamentos por dia (${range.start} → ${range.end})`}>
          <Table
            cols={["Data", "Total"]}
            rows={
              loading
                ? []
                : serie.map((r) => [r.data, r.total])
            }
            empty="Sem dados no período."
          />
        </Section>

        <Section title="Especialidades mais procuradas (30 dias)">
          <Table
            cols={["Especialidade", "Total"]}
            rows={
              loading
                ? []
                : ranking.map((r) => [r.especialidade, r.total])
            }
            empty="Sem dados."
          />
        </Section>
      </div>
    </div>
  );
}

function Kpi({ label, value }) {
  return (
    <div style={styles.kpi}>
      <div style={styles.kpiLabel}>{label}</div>
      <div style={styles.kpiValue}>{value ?? "—"}</div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ marginTop: 18 }}>
      <div style={styles.sectionTitle}>{title}</div>
      {children}
    </div>
  );
}

function Table({ cols, rows, empty }) {
  return (
    <div style={styles.card}>
      <table style={styles.table}>
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c} style={styles.th}>
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={cols.length} style={styles.tdMuted}>
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((r, i) => (
              <tr key={i}>
                {r.map((v, j) => (
                  <td key={j} style={styles.td}>
                    {v}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  header: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    flexWrap: "wrap",
  },
  h1: { fontSize: 22, fontWeight: 900, color: "#0f172a" },
  h2: { fontSize: 13, color: "#334155", marginTop: 4 },

  primaryBtn: {
    background: "#1d4ed8",
    color: "white",
    border: "1px solid #1d4ed8",
    borderRadius: 12,
    padding: "10px 14px",
    fontWeight: 900,
    cursor: "pointer",
  },

  alertErr: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    background: "#fff1f2",
    border: "1px solid #fecaca",
    color: "#991b1b",
    fontWeight: 800,
  },

  kpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
    gap: 12,
    marginTop: 16,
  },
  kpi: {
    background: "white",
    border: "1px solid #dbeafe",
    borderRadius: 16,
    padding: 14,
  },
  kpiLabel: { fontSize: 12, color: "#334155", fontWeight: 800 },
  kpiValue: { fontSize: 26, fontWeight: 950, marginTop: 6 },

  sectionTitle: { fontSize: 16, fontWeight: 900, marginBottom: 10 },

  twoCols: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
    marginTop: 16,
  },

  card: {
    background: "white",
    border: "1px solid #dbeafe",
    borderRadius: 16,
    overflow: "hidden",
  },

  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    textAlign: "left",
    padding: 10,
    fontSize: 12,
    color: "#334155",
    borderBottom: "1px solid #dbeafe",
    background: "#f8fbff",
  },
  td: {
    padding: 10,
    borderBottom: "1px solid #eef6ff",
    fontSize: 13,
  },
  tdMuted: {
    padding: 14,
    fontSize: 13,
    color: "#64748b",
    textAlign: "center",
  },
};
