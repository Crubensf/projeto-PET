import { useEffect, useState } from "react";
import {
  listarEspecialidades,
  listarProfissionais,
  listarLocais,
  listarSlots,
  criarAgendamento
} from "../services/agendamentoService";

export default function Agendamento() {
  const [especialidades, setEspecialidades] = useState([]);
  const [profissionais, setProfissionais] = useState([]);
  const [locais, setLocais] = useState([]);
  const [slots, setSlots] = useState([]);

  const [especialidadeId, setEspecialidadeId] = useState("");
  const [profissionalId, setProfissionalId] = useState("");
  const [localId, setLocalId] = useState("");
  const [modalidade, setModalidade] = useState("PRESENCIAL");
  const [data, setData] = useState("");

  useEffect(() => {
    listarEspecialidades().then(setEspecialidades);
    listarLocais().then(setLocais);
  }, []);

  useEffect(() => {
    if (especialidadeId) {
      listarProfissionais(especialidadeId, modalidade)
        .then(setProfissionais);
    }
  }, [especialidadeId, modalidade]);

  useEffect(() => {
    if (profissionalId && localId && data) {
      listarSlots(profissionalId, localId, data)
        .then(setSlots);
    }
  }, [profissionalId, localId, data]);

  async function confirmar(slot) {
    const payload = {
      paciente: {
        nome: "Paciente Teste",
        nome_mae: "Mae Teste",
        telefone: "999999999",
        municipio: "Teresina",
        data_nascimento: "2000-01-01"
      },
      profissional_id: profissionalId,
      local_id: localId,
      especialidade_id: especialidadeId,
      modalidade,
      inicio: slot.inicio,
      duracao_min: 30
    };

    await criarAgendamento(payload);
    alert("Agendamento realizado com sucesso");
  }

  return (
    <div>
      <h2>Agendamento UBS</h2>

      <select onChange={e => setEspecialidadeId(e.target.value)}>
        <option value="">Especialidade</option>
        {especialidades.map(e => (
          <option key={e.id} value={e.id}>{e.nome}</option>
        ))}
      </select>

      <select onChange={e => setModalidade(e.target.value)}>
        <option value="PRESENCIAL">Presencial</option>
        <option value="TELEMEDICINA">Telemedicina</option>
      </select>

      <select onChange={e => setProfissionalId(e.target.value)}>
        <option value="">Profissional</option>
        {profissionais.map(p => (
          <option key={p.id} value={p.id}>{p.nome}</option>
        ))}
      </select>

      <select onChange={e => setLocalId(e.target.value)}>
        <option value="">Local</option>
        {locais.map(l => (
          <option key={l.id} value={l.id}>{l.nome}</option>
        ))}
      </select>

      <input type="date" onChange={e => setData(e.target.value)} />

      <ul>
        {slots.map((s, i) => (
          <li key={i}>
            {new Date(s.inicio).toLocaleTimeString()}{" "}
            <button onClick={() => confirmar(s)}>Agendar</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
