import React, { useEffect, useMemo, useState } from "react";
import api from "../services/api";

const API_BASE = (import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000")
  .replace(/\/+$/, "");

function formatBR(iso) {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR");
}

function toInputDateTime(iso) {
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(
    d.getDate()
  )}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function toISOFromLocalInput(v) {
  return new Date(v).toISOString();
}

export default function AgendamentosCRUD() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [items, setItems] = useState([]);

  const [pacientes, setPacientes] = useState([]);
  const [profissionais, setProfissionais] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [locais, setLocais] = useState([]);

  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    paciente_id: "",
    profissional_id: "",
    especialidade_id: "",
    local_id: "",
    inicio: "",
    modalidade: "PRESENCIAL",
    status: "agendado",
  });
  const [saving, setSaving] = useState(false);

  const [isNarrow, setIsNarrow] = useState(
    () => (typeof window !== "undefined" ? window.innerWidth < 900 : false)
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    const onResize = () => setIsNarrow(window.innerWidth < 900);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const maps = useMemo(() => {
    const mPac = new Map(pacientes.map((p) => [String(p.id), p]));
    const mProf = new Map(profissionais.map((p) => [String(p.id), p]));
    const mEsp = new Map(especialidades.map((e) => [String(e.id), e]));
    const mLoc = new Map(locais.map((l) => [String(l.id), l]));
    return { mPac, mProf, mEsp, mLoc };
  }, [pacientes, profissionais, especialidades, locais]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;

    return items.filter((a) => {
      const pac = maps.mPac.get(String(a.paciente_id))?.nome || "";
      const prof = maps.mProf.get(String(a.profissional_id))?.nome || "";
      const esp = maps.mEsp.get(String(a.especialidade_id))?.nome || "";
      const loc = maps.mLoc.get(String(a.local_id))?.nome || "";

      return [
        a.id,
        a.modalidade,
        a.status,
        a.paciente_id,
        a.profissional_id,
        a.especialidade_id,
        a.local_id,
        a.inicio,
        pac,
        prof,
        esp,
        loc,
      ].some((x) => String(x ?? "").toLowerCase().includes(q));
    });
  }, [items, query, maps]);

  async function loadAll() {
    setLoading(true);
    setErr("");
    try {
      const [agRes, pacRes, profRes, espRes, locRes] = await Promise.all([
        api.get("/api/agendamentos"),
        api.get("/api/pacientes"),
        api.get("/api/profissionais"),
        api.get("/api/especialidades"),
        api.get("/api/locais"),
      ]);

      setItems(agRes || []);
      setPacientes(pacRes || []);
      setProfissionais(profRes || []);
      setEspecialidades(espRes || []);
      setLocais(locRes || []);
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  function startEdit(a) {
    setEditing(a);
    setForm({
      paciente_id: String(a.paciente_id ?? ""),
      profissional_id: String(a.profissional_id ?? ""),
      especialidade_id: String(a.especialidade_id ?? ""),
      local_id: String(a.local_id ?? ""),
      inicio: toInputDateTime(a.inicio),
      modalidade: a.modalidade ?? "PRESENCIAL",
      status: a.status ?? "agendado",
    });
    setErr("");
  }

  function cancelEdit() {
    setEditing(null);
    setForm({
      paciente_id: "",
      profissional_id: "",
      especialidade_id: "",
      local_id: "",
      inicio: "",
      modalidade: "PRESENCIAL",
      status: "agendado",
    });
  }

  function setF(key, value) {
    setForm((s) => ({ ...s, [key]: value }));
  }

  async function save() {
    if (!editing) return;

    setSaving(true);
    setErr("");
    try {
      const payload = {
        paciente_id: Number(form.paciente_id),
        profissional_id: Number(form.profissional_id),
        especialidade_id: Number(form.especialidade_id),
        local_id: Number(form.local_id),
        inicio: toISOFromLocalInput(form.inicio),
        modalidade: form.modalidade,
        status: form.status,
      };

      await api.put(`/api/agendamentos/${editing.id}`, payload);

      cancelEdit();
      await loadAll();
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    const ok = window.confirm(
      "Remover este agendamento? Essa ação não pode ser desfeita."
    );
    if (!ok) return;

    try {
      await api.del(`/api/agendamentos/${id}`);
      await loadAll();
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }

  async function cancelarPorStatus(a) {
    const ok = window.confirm("Cancelar este agendamento?");
    if (!ok) return;

    try {
      await api.put(`/api/agendamentos/${a.id}`, { status: "cancelado" });
      await loadAll();
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }

  function abrirBundleJson(id) {
    window.open(`${API_BASE}/fhir/bundle/agendamento/${id}`, "_blank");
  }

  function abrirComprovantePdf(id) {
    window.open(`${API_BASE}/fhir/bundle/comprovante/${id}`, "_blank");
  }

  return (
    <div>
      <div style={styles.pageHeader}>
        <div>
          <div style={styles.h1}>Gestão de agendamentos</div>
          <div style={styles.h2}>
            Gestão administrativa: editar, cancelar e remover agendamentos.
          </div>
        </div>

        <button onClick={loadAll} disabled={loading} style={styles.primaryBtn}>
          {loading ? "Carregando..." : "Recarregar"}
        </button>
      </div>

      {err ? (
        <div style={styles.alertErr}>
          <strong>Erro:</strong> {err}
        </div>
      ) : null}

      {editing ? (
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <div style={styles.cardTitle}>
              Editar agendamento #{editing.id}
            </div>
            <div style={styles.cardSubtitle}>
              Atualize os dados e salve as alterações.
            </div>
          </div>

          <div style={styles.cardBody}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isNarrow ? "1fr" : "1fr 1fr",
                gap: 10,
              }}
            >
              <FieldSelect
                label="Paciente"
                value={form.paciente_id}
                onChange={(v) => setF("paciente_id", v)}
                options={pacientes.map((p) => ({
                  value: String(p.id),
                  label: `${p.nome} (#${p.id})`,
                }))}
              />

              <FieldSelect
                label="Especialidade"
                value={form.especialidade_id}
                onChange={(v) => setF("especialidade_id", v)}
                options={especialidades.map((e) => ({
                  value: String(e.id),
                  label: e.nome,
                }))}
              />

              <FieldSelect
                label="Profissional"
                value={form.profissional_id}
                onChange={(v) => setF("profissional_id", v)}
                options={profissionais.map((p) => ({
                  value: String(p.id),
                  label: p.nome,
                }))}
              />

              <FieldSelect
                label="Local"
                value={form.local_id}
                onChange={(v) => setF("local_id", v)}
                options={locais.map((l) => ({
                  value: String(l.id),
                  label: `${l.nome} — ${l.municipio}`,
                }))}
              />

              <Field
                label="Início"
                type="datetime-local"
                value={form.inicio}
                onChange={(v) => setF("inicio", v)}
              />

              <FieldSelect
                label="Modalidade"
                value={form.modalidade}
                onChange={(v) => setF("modalidade", v)}
                options={[
                  { value: "PRESENCIAL", label: "Presencial" },
                  { value: "TELEMEDICINA", label: "Telemedicina" },
                ]}
              />

              <FieldSelect
                label="Situação"
                value={form.status}
                onChange={(v) => setF("status", v)}
                options={[
                  { value: "agendado", label: "Confirmado" },
                  { value: "cancelado", label: "Cancelado" },
                  { value: "atendido", label: "Atendido" },
                ]}
              />
            </div>

            <div style={styles.actionsRow}>
              <button
                onClick={save}
                disabled={saving}
                style={styles.primaryBtn}
              >
                {saving ? "Salvando..." : "Salvar"}
              </button>
              <button onClick={cancelEdit} style={styles.secondaryBtn}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <div style={styles.card}>
        <div style={styles.listHeader}>
          <strong>Lista</strong>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por paciente, profissional, especialidade, local, status..."
            style={styles.search}
          />
        </div>

        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              minWidth: 1200,
            }}
          >
            <thead>
              <tr style={{ background: "#f8fbff" }}>
                <Th>ID</Th>
                <Th>Início</Th>
                <Th>Paciente</Th>
                <Th>Especialidade</Th>
                <Th>Profissional</Th>
                <Th>Local</Th>
                <Th>Modalidade</Th>
                <Th>Situação</Th>
                <Th>Ações</Th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <Td colSpan={9}>Carregando…</Td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <Td colSpan={9}>Nenhum agendamento encontrado.</Td>
                </tr>
              ) : (
                filtered.map((a) => {
                  const pac =
                    maps.mPac.get(String(a.paciente_id))?.nome ||
                    `#${a.paciente_id}`;
                  const esp =
                    maps.mEsp.get(String(a.especialidade_id))?.nome ||
                    `#${a.especialidade_id}`;
                  const prof =
                    maps.mProf.get(String(a.profissional_id))?.nome ||
                    `#${a.profissional_id}`;
                  const loc =
                    maps.mLoc.get(String(a.local_id))?.nome ||
                    `#${a.local_id}`;

                  return (
                    <tr key={a.id}>
                      <Td>{a.id}</Td>
                      <Td>{formatBR(a.inicio)}</Td>
                      <Td>{pac}</Td>
                      <Td>{esp}</Td>
                      <Td>{prof}</Td>
                      <Td>{loc}</Td>
                      <Td>
                        {a.modalidade === "TELEMEDICINA"
                          ? "Telemedicina"
                          : "Presencial"}
                      </Td>
                      <Td>{a.status}</Td>
                      <Td>
                        <div
                          style={{
                            display: "flex",
                            gap: 8,
                            flexWrap: "wrap",
                          }}
                        >
                          <button
                            onClick={() => startEdit(a)}
                            style={styles.smallBtn}
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => cancelarPorStatus(a)}
                            style={styles.smallBtnWarn}
                          >
                            Cancelar
                          </button>
                          <button
                            onClick={() => remove(a.id)}
                            style={styles.smallBtnDanger}
                          >
                            Remover
                          </button>
                          <button
                            onClick={() => abrirBundleJson(a.id)}
                            style={styles.smallBtnInfo}
                          >
                            Bundle JSON
                          </button>
                          <button
                            onClick={() => abrirComprovantePdf(a.id)}
                            style={styles.smallBtnPdf}
                          >
                            PDF
                          </button>
                        </div>
                      </Td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div style={styles.footnote}>
        Cancelar altera a situação para cancelado e “Remover” exclui o registro.
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text" }) {
  return (
    <label style={{ display: "block" }}>
      <div style={styles.label}>{label}</div>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={styles.input}
      />
    </label>
  );
}

function FieldSelect({ label, value, onChange, options }) {
  return (
    <label style={{ display: "block" }}>
      <div style={styles.label}>{label}</div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={styles.select}
      >
        <option value="" disabled>
          Selecione...
        </option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function Th({ children }) {
  return <th style={styles.th}>{children}</th>;
}
function Td({ children, colSpan }) {
  return (
    <td colSpan={colSpan} style={styles.td}>
      {children}
    </td>
  );
}

const styles = {
  pageHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-end",
    gap: 12,
    flexWrap: "wrap",
    marginBottom: 12,
  },
  h1: { fontSize: 22, fontWeight: 950, color: "#0f172a" },
  h2: { fontSize: 13, color: "#334155", marginTop: 6, maxWidth: 720 },

  card: {
    background: "white",
    border: "1px solid #dbeafe",
    borderRadius: 18,
    overflow: "hidden",
    boxShadow: "0 10px 25px rgba(15, 23, 42, 0.08)",
    marginTop: 12,
  },
  cardHeader: { padding: "16px 16px 10px" },
  cardTitle: { fontSize: 15, fontWeight: 950, color: "#0f172a" },
  cardSubtitle: { fontSize: 12, color: "#334155", marginTop: 6 },
  cardBody: { padding: 16 },

  alertErr: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    border: "1px solid #fecaca",
    background: "#fff1f2",
    color: "#991b1b",
    fontWeight: 800,
  },

  label: {
    fontSize: 12,
    color: "#334155",
    fontWeight: 900,
    marginBottom: 6,
  },
  input: {
    width: "100%",
    padding: 10,
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    background: "white",
    outline: "none",
  },
  select: {
    width: "100%",
    padding: 10,
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    background: "white",
    outline: "none",
  },

  actionsRow: {
    display: "flex",
    gap: 10,
    marginTop: 12,
    flexWrap: "wrap",
  },
  primaryBtn: {
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid #1d4ed8",
    background: "#1d4ed8",
    color: "white",
    fontWeight: 900,
    cursor: "pointer",
  },
  secondaryBtn: {
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    background: "white",
    color: "#0f172a",
    fontWeight: 900,
    cursor: "pointer",
  },

  listHeader: {
    padding: 12,
    borderBottom: "1px solid #dbeafe",
    display: "flex",
    justifyContent: "space-between",
    gap: 10,
    alignItems: "center",
    flexWrap: "wrap",
  },
  search: {
    padding: 10,
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    width: 520,
    maxWidth: "100%",
    outline: "none",
  },

  th: {
    textAlign: "left",
    padding: 10,
    fontSize: 12,
    color: "#334155",
    borderBottom: "1px solid #dbeafe",
    whiteSpace: "nowrap",
  },
  td: {
    padding: 10,
    borderBottom: "1px solid #eef6ff",
    fontSize: 13,
    color: "#0f172a",
    verticalAlign: "top",
    whiteSpace: "nowrap",
  },

  smallBtn: {
    padding: "6px 10px",
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    background: "white",
    fontWeight: 900,
    cursor: "pointer",
  },
  smallBtnWarn: {
    padding: "6px 10px",
    borderRadius: 12,
    border: "1px solid #fed7aa",
    background: "#ffedd5",
    color: "#9a3412",
    fontWeight: 900,
    cursor: "pointer",
  },
  smallBtnDanger: {
    padding: "6px 10px",
    borderRadius: 12,
    border: "1px solid #fecaca",
    background: "#fff1f2",
    color: "#991b1b",
    fontWeight: 900,
    cursor: "pointer",
  },
  smallBtnInfo: {
    padding: "6px 10px",
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    background: "#eff6ff",
    color: "#1d4ed8",
    fontWeight: 900,
    cursor: "pointer",
  },
  smallBtnPdf: {
    padding: "6px 10px",
    borderRadius: 12,
    border: "1px solid #c7d2fe",
    background: "#eef2ff",
    color: "#3730a3",
    fontWeight: 900,
    cursor: "pointer",
  },

  footnote: {
    marginTop: 12,
    color: "#334155",
    fontSize: 12,
    fontWeight: 700,
  },
};
