
import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";

import Dashboard from "./pages/Dashboard";
import Agendamento from "./pages/Agendamento";
import AgendamentosCRUD from "./pages/AgendamentosCRUD";
import Pacientes from "./pages/Pacientes";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agendamento" element={<Agendamento />} />
          <Route path="/agendamentos-crud" element={<AgendamentosCRUD />} />
          <Route path="/pacientes" element={<Pacientes />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
