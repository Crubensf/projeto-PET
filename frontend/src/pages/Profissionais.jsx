
import React, { useEffect, useMemo, useRef, useState } from "react";
import api from "../services/api";

function initialForm() {
  return {
    nome: "",
    especialidade_id: "",
    crm: "",
    crm_uf: "",
    ativo: true,
  };
}

export default function Profissionais() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [items, setItems] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);

  const [query, setQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(initialForm());
  const [saving, setSaving] = useState(false);

  const formRef = useRef(null);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    if (!q) return items;

    return items.filter((p) =>
      [
        p.nome,
        p.crm,
        p.crm_uf,
        especialidades.find((e) => e.id === p.especialidade_id)?.nome ?? "",
      ].some((v) => String(v ?? "").toLowerCase().includes(q))
    );
  }, [items, query, especialidades]);

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const [prof, esp] = await Promise.all([
        api.get("/api/profissionais"),
        api.get("/api/especialidades"),
      ]);

      
      setItems(Array.isArray(prof) ? prof : prof?.data ?? []);
      setEspecialidades(Array.isArray(esp) ? esp : esp?.data ?? []);
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startEdit(p) {
    setEditingId(p.id);
    setForm({
      nome: p.nome ?? "",
      especialidade_id: String(p.especialidade_id ?? ""),
      crm: p.crm ?? "",
      crm_uf: p.crm_uf ?? "",
      ativo: Boolean(p.ativo),
    });

    setErr("");
    
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  }

  function resetForm() {
    setForm(initialForm());
    setEditingId(null);
    setErr("");
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setErr("");

    const payload = {
      nome: form.nome,
      especialidade_id: Number(form.especialidade_id),
      crm: form.crm || null,
      crm_uf: form.crm_uf || null,
      ativo: Boolean(form.ativo),
    };

    try {
      if (editingId) {
        await api.put(`/api/profissionais/${editingId}`, payload);
      } else {
        await api.post("/api/profissionais", payload);
      }

      resetForm();
      await load();
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setSaving(false);
    }
  }

  async function removeProfissional(p) {
    const ok = window.confirm(
      `Excluir o profissional "${p.nome}"?\n\nSe existir agendamento vinculado a ele, a exclusão pode ser bloqueada.`
    );
    if (!ok) return;

    setErr("");
    try {
      
      await api.del(`/api/profissionais/${p.id}`);

      if (editingId === p.id) resetForm();
      await load();
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <div style={styles.h1}>Profissionais</div>
          <div style={styles.h2}>
            Cadastro e gerenciamento de profissionais de saúde
          </div>
        </div>

        <button onClick={resetForm} type="button" style={styles.secondaryBtn}>
          Novo profissional
        </button>
      </div>

      {err ? <div style={styles.alertErr}>{err}</div> : null}

      {/* FORMULÁRIO STICKY */}
      <form
        ref={formRef}
        onSubmit={submit}
        style={{ ...styles.card, ...styles.stickyForm }}
      >
        <div style={styles.formTopRow}>
          <div style={styles.formTitle}>
            {editingId ? `Editando #${editingId}` : "Novo profissional"}
          </div>
          {editingId ? (
            <button
              type="button"
              onClick={resetForm}
              disabled={saving}
              style={styles.ghostBtn}
            >
              Cancelar edição
            </button>
          ) : null}
        </div>

        <div style={styles.formGrid}>
          <Field
            label="Nome"
            value={form.nome}
            onChange={(v) => setForm({ ...form, nome: v })}
          />

          <FieldSelect
            label="Especialidade"
            value={form.especialidade_id}
            onChange={(v) => setForm({ ...form, especialidade_id: v })}
            options={especialidades.map((e) => ({
              value: String(e.id),
              label: e.nome,
            }))}
          />

          <Field
            label="CRM"
            value={form.crm}
            onChange={(v) => setForm({ ...form, crm: v })}
          />

          <Field
            label="UF do CRM"
            value={form.crm_uf}
            maxLength={2}
            onChange={(v) => setForm({ ...form, crm_uf: v.toUpperCase() })}
          />

          <label
            style={{
              ...styles.field,
              gridColumn: "1 / -1",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <input
              type="checkbox"
              checked={form.ativo}
              onChange={(e) => setForm({ ...form, ativo: e.target.checked })}
            />
            <span style={styles.checkboxLabel}>Profissional ativo</span>
          </label>
        </div>

        <div style={styles.actions}>
          <button type="submit" disabled={saving} style={styles.primaryBtn}>
            {saving ? "Salvando..." : editingId ? "Salvar" : "Cadastrar"}
          </button>
        </div>
      </form>

      <div style={{ marginTop: 16 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar profissional, CRM, especialidade..."
          style={styles.search}
        />
      </div>

      <div style={styles.card}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Nome</th>
              <th style={styles.th}>Especialidade</th>
              <th style={styles.th}>CRM</th>
              <th style={styles.th}>Ativo</th>
              <th style={styles.th}>Ações</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} style={styles.tdMuted}>
                  Carregando…
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={5} style={styles.tdMuted}>
                  Nenhum profissional.
                </td>
              </tr>
            ) : (
              filtered.map((p) => {
                const esp =
                  especialidades.find((e) => e.id === p.especialidade_id)?.nome ||
                  `#${p.especialidade_id}`;

                const crmStr =
                  p.crm && p.crm_uf ? `${p.crm} - ${p.crm_uf}` : p.crm || "-";

                return (
                  <tr key={p.id}>
                    <td style={styles.td}>{p.nome}</td>
                    <td style={styles.td}>{esp}</td>
                    <td style={styles.td}>{crmStr}</td>
                    <td style={styles.td}>{p.ativo ? "Sim" : "Não"}</td>
                    <td style={styles.td}>
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <button
                          type="button"
                          onClick={() => startEdit(p)}
                          style={styles.smallBtn}
                        >
                          Editar
                        </button>

                        <button
                          type="button"
                          onClick={() => removeProfissional(p)}
                          style={styles.smallBtnDanger}
                        >
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        <div style={styles.tableHint}>
          Dica: se a exclusão falhar, geralmente é porque existem agendamentos
          vinculados ao profissional (restrição de chave estrangeira).
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text", maxLength }) {
  return (
    <label style={styles.field}>
      <div style={styles.label}>{label}</div>
      <input
        type={type}
        value={value}
        maxLength={maxLength}
        onChange={(e) => onChange(e.target.value)}
        style={styles.input}
      />
    </label>
  );
}

function FieldSelect({ label, value, onChange, options }) {
  return (
    <label style={styles.field}>
      <div style={styles.label}>{label}</div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={styles.input}
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

const styles = {
  page: {
    boxSizing: "border-box",
    maxWidth: 1200,
    margin: "0 auto",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 12,
    flexWrap: "wrap",
  },
  h1: { fontSize: 22, fontWeight: 900 },
  h2: { fontSize: 13, color: "#334155" },

  card: {
    boxSizing: "border-box",
    background: "white",
    border: "1px solid #dbeafe",
    borderRadius: 16,
    padding: 16,
    marginTop: 16,
  },


  stickyForm: {
    position: "sticky",
    top: 90,
    zIndex: 10,
    boxShadow: "0 12px 30px rgba(15, 23, 42, 0.10)",
  },

  formTopRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 10,
    flexWrap: "wrap",
    marginBottom: 10,
  },
  formTitle: {
    fontSize: 13,
    fontWeight: 900,
    color: "#0f172a",
  },

  formGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 12,
    alignItems: "start",
  },

  field: {
    display: "block",
    minWidth: 0,
    boxSizing: "border-box",
  },

  label: {
    fontSize: 12,
    fontWeight: 800,
    marginBottom: 6,
  },

  input: {
    boxSizing: "border-box",
    minWidth: 0,
    width: "100%",
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    outline: "none",
  },

  checkboxLabel: {
    fontSize: 12,
    fontWeight: 800,
    color: "#334155",
  },

  actions: {
    marginTop: 12,
    display: "flex",
    justifyContent: "flex-end",
    gap: 10,
    flexWrap: "wrap",
  },

  primaryBtn: {
    background: "#1d4ed8",
    color: "white",
    border: "1px solid #1d4ed8",
    borderRadius: 12,
    padding: "10px 14px",
    fontWeight: 900,
    cursor: "pointer",
  },

  secondaryBtn: {
    background: "white",
    border: "1px solid #bfdbfe",
    borderRadius: 12,
    padding: "10px 14px",
    fontWeight: 900,
    cursor: "pointer",
  },

  ghostBtn: {
    background: "transparent",
    border: "1px solid #bfdbfe",
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
  },

  search: {
    boxSizing: "border-box",
    width: "100%",
    padding: 10,
    borderRadius: 12,
    border: "1px solid #bfdbfe",
    outline: "none",
  },

  table: { width: "100%", borderCollapse: "collapse" },
  th: { padding: 10, borderBottom: "1px solid #dbeafe", textAlign: "left" },
  td: { padding: 10, borderBottom: "1px solid #eef6ff" },
  tdMuted: { padding: 12, textAlign: "center", color: "#64748b" },

  smallBtn: {
    padding: "6px 10px",
    borderRadius: 10,
    border: "1px solid #bfdbfe",
    background: "white",
    fontWeight: 800,
    cursor: "pointer",
  },

  smallBtnDanger: {
    padding: "6px 10px",
    borderRadius: 10,
    border: "1px solid #fecaca",
    background: "#fff1f2",
    color: "#991b1b",
    fontWeight: 800,
    cursor: "pointer",
  },

  tableHint: {
    marginTop: 10,
    fontSize: 12,
    color: "#64748b",
    fontWeight: 600,
  },
};
