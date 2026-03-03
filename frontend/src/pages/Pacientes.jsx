
import React, { useEffect, useMemo, useRef, useState } from "react";
import { pacienteService } from "../services/pacienteService";

function onlyDigits(v) {
  return String(v ?? "").replace(/\D+/g, "");
}
function clampDigits(v, max) {
  return onlyDigits(v).slice(0, max);
}
function clampCPF(v) {
  return onlyDigits(v).slice(0, 11);
}


function initialForm() {
  return {
    nome: "",
    cpf: "",
    cartao_sus: "",
    telefone: "",
    data_nascimento: "",
    municipio: "",
    endereco: "",
    nome_mae: "",
  };
}

export default function Pacientes() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [items, setItems] = useState([]);

  const [query, setQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(initialForm());
  const [saving, setSaving] = useState(false);

  const formRef = useRef(null);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    if (!q) return items;
    return items.filter((p) =>
      [p.nome, p.municipio, p.cartao_sus, p.telefone, p.cpf].some((v) =>
        String(v ?? "").toLowerCase().includes(q)
      )
    );
  }, [items, query]);

  async function load() {
    setLoading(true);
    setErr("");
    try {
      setItems(await pacienteService.list());
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
      cpf: String(p.cpf ?? ""),
      cartao_sus: String(p.cartao_sus ?? ""),
      telefone: String(p.telefone ?? ""),
      data_nascimento: (p.data_nascimento ?? "").slice(0, 10),
      municipio: p.municipio ?? "",
      endereco: p.endereco ?? "",
      nome_mae: p.nome_mae ?? "",
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

  async function removePaciente(p) {
    const ok = window.confirm(
      `Excluir o paciente "${p.nome}"?\n\nSe existir agendamento vinculado a ele, a exclusão pode ser bloqueada.`
    );
    if (!ok) return;

    setErr("");
    try {
      await pacienteService.remove(p.id);
      if (editingId === p.id) resetForm();
      await load();
    } catch (e) {
      setErr(String(e?.message || e));
    }
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setErr("");

    const payload = {
      ...form,
      cartao_sus: clampDigits(form.cartao_sus, 15),
      telefone: clampDigits(form.telefone, 11),
    };

    try {
      if (editingId) {
        await pacienteService.update(editingId, payload);
      } else {
        await pacienteService.create(payload);
      }

      resetForm();
      await load();
    } catch (e) {
      setErr(String(e?.message || e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <div style={styles.h1}>Pacientes</div>
          <div style={styles.h2}>Cadastro e gerenciamento de pacientes</div>
        </div>

        <button onClick={resetForm} type="button" style={styles.secondaryBtn}>
          Novo paciente
        </button>
      </div>

      {err ? <div style={styles.alertErr}>{err}</div> : null}

      {/* FORMULÁRIO STICKY */}
      <form
        ref={formRef}
        onSubmit={submit}
        style={{ ...styles.card}}
      >
        <div style={styles.formTopRow}>
          <div style={styles.formTitle}>
            {editingId ? `Editando #${editingId}` : "Novo paciente"}
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
          <Field
            label="Nome da mãe"
            value={form.nome_mae}
            onChange={(v) => setForm({ ...form, nome_mae: v })}
          />
          <Field
            label="CPF"
            value={form.cpf}
            inputMode="numeric"
            maxLength={11}
            onChange={(v) =>
              setForm({ ...form, cpf: clampCPF(v) })
            }
          />

          <Field
            label="Cartão SUS"
            value={form.cartao_sus}
            inputMode="numeric"
            maxLength={15}
            onChange={(v) =>
              setForm({ ...form, cartao_sus: clampDigits(v, 15) })
            }
          />
          <Field
            label="Telefone"
            value={form.telefone}
            inputMode="numeric"
            maxLength={11}
            onChange={(v) =>
              setForm({ ...form, telefone: clampDigits(v, 11) })
            }
          />

          <Field
            type="date"
            label="Nascimento"
            value={form.data_nascimento}
            onChange={(v) => setForm({ ...form, data_nascimento: v })}
          />
          <Field
            label="Município"
            value={form.municipio}
            onChange={(v) => setForm({ ...form, municipio: v })}
          />

          <Field
            label="Endereço"
            full
            value={form.endereco}
            onChange={(v) => setForm({ ...form, endereco: v })}
          />
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
          placeholder="Buscar paciente..."
          style={styles.search}
        />
      </div>

      <div style={styles.card}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Nome</th>
              <th style={styles.th}>CNS</th>
              <th style={styles.th}>CPF</th>
              <th style={styles.th}>Telefone</th>
              <th style={styles.th}>Município</th>
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
                  Nenhum paciente.
                </td>
              </tr>
            ) : (
              filtered.map((p) => (
                <tr key={p.id}>
                  <td style={styles.td}>{p.nome}</td>
                  <td style={styles.td}>{p.cartao_sus}</td>
                  <td style={styles.td}>{p.cpf}</td>
                  <td style={styles.td}>{p.telefone}</td>
                  <td style={styles.td}>{p.municipio}</td>
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
                        onClick={() => removePaciente(p)}
                        style={styles.smallBtnDanger}
                      >
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        <div style={styles.tableHint}>
          Dica: se a exclusão falhar, geralmente é porque existem agendamentos
          vinculados ao paciente (restrição de chave estrangeira).
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  full,
  inputMode,
  maxLength,
}) {
  return (
    <label
      style={{
        ...styles.field,
        gridColumn: full ? "1 / -1" : "auto",
      }}
    >
      <div style={styles.label}>{label}</div>
      <input
        type={type}
        value={value}
        inputMode={inputMode}
        maxLength={maxLength}
        onChange={(e) => onChange(e.target.value)}
        style={styles.input}
      />
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
