// pacienteService.js
import api from "./api";

export const pacienteService = {
  list() {
    return api.get("/api/pacientes");
  },
  get(id) {
    return api.get(`/api/pacientes/${id}`);
  },
  getByCns(cns) {
    return api.get(`/api/pacientes/by-cns/${cns}`);
  },
  create(payload) {
    return api.post("/api/pacientes", payload);
  },
  update(id, payload) {
    return api.put(`/api/pacientes/${id}`, payload);
  },
  remove(id) {
    return api.del(`/api/pacientes/${id}`);
  },
};
