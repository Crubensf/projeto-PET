import api from "./api";

function onlyDigits(v) {
  return String(v ?? "").replace(/\D+/g, "");
}

export async function carregarCatalogos() {
  const [especialidades, locais, profissionaisAll] = await Promise.all([
    api.get("/api/especialidades"),
    api.get("/api/locais"),
    api.get("/api/profissionais"),
  ]);

  return { especialidades, locais, profissionaisAll };
}

export async function carregarProfissionais(especialidadeId) {
  
  const all = await api.get("/api/profissionais");
  const id = Number(especialidadeId);
  return all.filter((p) => Number(p.especialidade_id) === id);
}

export async function carregarSlots(profissionalId, dateStr) {
  
  const params = new URLSearchParams({
    profissional_id: String(profissionalId),
    date: String(dateStr),
  });
  return api.get(`/api/slots?${params.toString()}`);
}

export async function cadastrarPaciente(paciente) {
  // Blindagem para CNS/telefone no fluxo cidadão
  const payload = {
    ...paciente,
    cartao_sus: onlyDigits(paciente.cartao_sus),
    telefone: onlyDigits(paciente.telefone),
  };
  return api.post("/api/pacientes", payload);
}

export async function criarAgendamento(agendamento) {
  return api.post("/api/agendamentos", agendamento);
}
