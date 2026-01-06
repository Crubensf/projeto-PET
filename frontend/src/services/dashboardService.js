import { apiFetch } from "./api";

export const dashboardService = {
  resumo() {
    return apiFetch("/api/dashboard/resumo");
  },

  proximos(limit = 10) {
    return apiFetch(`/api/dashboard/proximos?limit=${limit}`);
  },

  porDia({ start, end } = {}) {
    const params = new URLSearchParams();
    if (start) params.set("start", start);
    if (end) params.set("end", end);
    const qs = params.toString();
    return apiFetch(`/api/dashboard/agendamentos/por-dia${qs ? `?${qs}` : ""}`);
  },

  porEspecialidade({ start, end, limit = 10 } = {}) {
    const params = new URLSearchParams();
    if (start) params.set("start", start);
    if (end) params.set("end", end);
    params.set("limit", String(limit));
    return apiFetch(`/api/dashboard/agendamentos/por-especialidade?${params.toString()}`);
  },
};
