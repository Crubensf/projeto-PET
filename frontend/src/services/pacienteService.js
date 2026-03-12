import api from "./api";
import { sanitizeCnsDigits, sanitizeCpfDigits } from "../utils/validation";

export const pacienteService = {
  async list() {
    return api.get("/api/pacientes");
  },

  async get(id) {
    return api.get(`/api/pacientes/${id}`);
  },

  async getByCns(cns) {
    return api.get(`/api/pacientes/by-cns/${sanitizeCnsDigits(cns)}`);
  },

  async getByCpf(cpf) {
    return api.get(`/api/pacientes/by-cpf/${sanitizeCpfDigits(cpf)}`);
  },

  async create(payload) {
    return api.post("/api/pacientes", payload);
  },

  async update(id, payload) {
    return api.put(`/api/pacientes/${id}`, payload);
  },

  async remove(id) {
  return api.del(`/api/pacientes/${id}`);
},
};
