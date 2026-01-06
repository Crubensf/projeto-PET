import { apiGet, apiPost, apiPatch } from "./api";

export const listarEspecialidades = () =>
  apiGet("/api/especialidades");

export const listarProfissionais = (especialidadeId, modalidade) =>
  apiGet(
    `/api/profissionais?especialidade_id=${especialidadeId}&modalidade=${modalidade}`
  );

export const listarLocais = () =>
  apiGet("/api/locais");

export const listarSlots = (profissionalId, localId, data) =>
  apiGet(
    `/api/slots?profissional_id=${profissionalId}&local_id=${localId}&data=${data}`
  );

export const criarAgendamento = (payload) =>
  apiPost("/api/agendamentos", payload);

export const cancelarAgendamento = (id) =>
  apiPatch(`/api/agendamentos/${id}/cancelar`);
