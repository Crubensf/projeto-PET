import React, { useCallback, useEffect, useMemo, useState } from "react";
import { dashboardService } from "../services/dashboardService";
import InfoCard from "../components/InfoCard";

function formatBRDateTime(iso) {
  return new Date(iso).toLocaleString("pt-BR");
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
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
    <div className="space-y-8">

      {/* HEADER */}
      <div className="flex justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Dashboard
          </h1>
          <p className="text-gray-500">
            Visão geral do sistema de agendamento
          </p>
        </div>

        <button
          onClick={load}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          {loading ? "Atualizando..." : "Atualizar"}
        </button>
      </div>

      {err && (
        <div className="bg-red-100 border border-red-300 text-red-700 p-4 rounded-lg">
          {err}
        </div>
      )}

      {/* RESUMO GERAL */}
      <InfoCard title="Resumo Geral">
        <Table
          cols={[
            "Pacientes",
            "Profissionais",
            "Especialidades",
            "Locais",
            "Agendamentos",
            "Hoje",
          ]}
          rows={
            loading || !resumo
              ? []
              : [[
                  resumo.total_pacientes,
                  resumo.total_profissionais,
                  resumo.total_especialidades,
                  resumo.total_locais,
                  resumo.total_agendamentos,
                  resumo.agendamentos_hoje,
                ]]
          }
          empty={loading ? "Carregando..." : "Sem dados."}
        />
      </InfoCard>

      {/* PRÓXIMOS AGENDAMENTOS */}
      <InfoCard title="Próximos agendamentos">
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
          empty={loading ? "Carregando..." : "Nenhum agendamento futuro."}
        />
      </InfoCard>

      {/* TABELAS INFERIORES */}
      <div className="grid md:grid-cols-2 gap-6">

        <InfoCard title={`Agendamentos por dia (${range.start} → ${range.end})`}>
          <Table
            cols={["Data", "Total"]}
            rows={loading ? [] : serie.map((r) => [new Date(r.data).toLocaleDateString("pt-BR"), r.total])}
            empty={loading ? "Carregando..." : "Sem dados no período."}
          />
        </InfoCard>

        <InfoCard title="Especialidades mais procuradas (30 dias)">
          <Table
            cols={["Especialidade", "Total"]}
            rows={loading ? [] : ranking.map((r) => [r.especialidade, r.total])}
            empty={loading ? "Carregando..." : "Sem dados."}
          />
        </InfoCard>

      </div>
    </div>
  );
}

/* ---------- TABELA PADRÃO ---------- */

function Table({ cols, rows, empty }) {
  return (
    <div className="bg-white rounded-lg overflow-hidden text-center">
      <table className="w-full border-collapse">
        <thead className="bg-blue-50">
          <tr>
            {cols.map((c) => (
              <th key={c} className="text-center text-sm p-3 border-b">
                {c}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={cols.length} className="p-4 text-center text-gray-500">
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((r, i) => (
              <tr key={i} className="border-b last:border-none hover:bg-gray-50">
                {r.map((v, j) => (
                  <td key={j} className="p-3 text-sm text-center font-semibold">
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
