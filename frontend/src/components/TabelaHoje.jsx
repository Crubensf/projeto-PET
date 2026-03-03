import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import api from "../services/api";

export default function TabelaHoje() {
  const [agendamentos, setAgendamentos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await api.get("/api/agendamentos/hoje");
        setAgendamentos(data);
      } catch (error) {
        console.error("Erro ao buscar agendamentos:", error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <p className="text-gray-500">Carregando...</p>;
  }

  if (!agendamentos.length) {
    return (
      <p className="text-gray-500 flex items-center gap-2">
        <Calendar className="w-4 h-4" />
        Nenhum agendamento para hoje.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left border-collapse">
        <thead>
          <tr className="border-b text-gray-600">
            <th className="py-2">Horário</th>
            <th className="py-2">Paciente</th>
            <th className="py-2">Profissional</th>
            <th className="py-2">Especialidade</th>
            <th className="py-2">Status</th>
          </tr>
        </thead>

        <tbody>
          {agendamentos.map((ag) => (
            <tr
              key={ag.id}
              className="border-b hover:bg-gray-50 transition"
            >
              <td className="py-2">
                {new Date(ag.inicio).toLocaleTimeString("pt-BR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </td>

              <td className="py-2">{ag.paciente_nome}</td>
              <td className="py-2">{ag.profissional_nome}</td>
              <td className="py-2">{ag.especialidade_nome}</td>

              <td className="py-2">
                <span className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-700">
                  {ag.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}