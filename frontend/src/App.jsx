import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";

import Dashboard from "./pages/Dashboard";
import Agendamento from "./pages/Agendamento";
import AgendamentosCRUD from "./pages/AgendamentosCRUD";
import Pacientes from "./pages/Pacientes";
import Profissionais from "./pages/Profissionais";
import Login from "./pages/Login";
import UsuarioCadastro from "./pages/UsuarioCadastro";

function RequireAuth({ children }) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rotas públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro-usuario" element={<UsuarioCadastro />} />

        {/* Rotas protegidas com layout */}
        <Route
          element={
            <RequireAuth>
              <AppShell />
            </RequireAuth>
          }
        >
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agendamento" element={<Agendamento />} />
          <Route path="/agendamentos-crud" element={<AgendamentosCRUD />} />
          <Route path="/pacientes" element={<Pacientes />} />
          <Route path="/profissionais" element={<Profissionais />} />
        </Route>

        {/* Fallback: se nenhuma rota bater, manda para /login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
