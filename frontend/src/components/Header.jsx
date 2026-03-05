import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  Calendar,
  LayoutDashboard,
  ClipboardList,
  Users,
  Stethoscope,
  LogOut,
  Home,
} from "lucide-react";

import logoPet from "../assets/logopet.png";

export default function Header() {
  const navigate = useNavigate();

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  function handleLogout() {
    localStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  }

  function NavItem({ to, icon: Icon, children }) {
    return (
      <NavLink
        to={to}
        className={({ isActive }) =>
          `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition
          ${
            isActive
              ? "bg-white text-blue-700 shadow"
              : "text-white hover:bg-white/20"
          }`
        }
      >
        <Icon className="w-4 h-4" />
        {children}
      </NavLink>
    );
  }

  return (
    <header className="shadow-md">

      {/* ===== FAIXA SUPERIOR ===== */}
      <div className="bg-blue-600 text-white">
        <div className="max-w-6xl mx-auto px-6 py-2 text-sm font-medium text-center">
          PET-Saúde • Sistema de Agendamento UBS
        </div>
      </div>

      {/* ===== ÁREA BRANCA COM LOGO ===== */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">

          <Link to="/" className="flex items-center gap-4">

            <img
              src={logoPet}
              alt="PET Saúde"
              className="w-20 h-20 object-contain"
            />

            <h1 className="text-xl font-semibold text-blue-900">
              Sistema de Agendamento UBS
            </h1>

          </Link>

          {token && (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-50 text-red-600 px-4 py-2 rounded-lg font-semibold hover:bg-red-100 transition"
            >
              <LogOut className="w-4 h-4" />
              Sair
            </button>
          )}

        </div>
      </div>

      {/* ===== NAVBAR ===== */}
      {token && (
        <nav className="bg-blue-600 text-white shadow-sm">
          <div className="max-w-6xl mx-auto px-6 py-2 flex flex-wrap gap-2 justify-center items-center">

            <NavItem to="/" icon={Home}>
              Início
            </NavItem>

            <NavItem to="/dashboard" icon={LayoutDashboard}>
              Dashboard
            </NavItem>

            <NavItem to="/agendamento" icon={Calendar}>
              Agendar
            </NavItem>

            <NavItem to="/agendamentos-crud" icon={ClipboardList}>
              Gerenciar Agendamentos
            </NavItem>

            <NavItem to="/pacientes" icon={Users}>
              Gerenciar Pacientes
            </NavItem>

            <NavItem to="/profissionais" icon={Stethoscope}>
              Gerenciar Profissionais
            </NavItem>

          </div>
        </nav>
      )}
    </header>
  );
}
