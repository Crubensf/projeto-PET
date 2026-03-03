import {
  UserPlus,
  ClipboardList,
  CalendarPlus,
  Search,
  ListChecks,
} from "lucide-react";

import Card from "../components/Card";
import TabelaHoje from "../components/TabelaHoje";
import InfoCard from "../components/InfoCard";
import { Calendar } from "lucide-react";

export default function PageHome() {
  return (
    <div className="max-w-7xl mx-auto p-8 space-y-12">

      {/* Mensagem de boas-vindas */}
      <section className="p-6 text-center">
        <h1 className="text-3xl font-bold text-blue-700">
          Bem-vindo ao Sistema de Agendamento UBS
        </h1>
        <p className="mt-2 text-gray-600">
          Sistema piloto desenvolvido no âmbito do PET-Saúde,
          com foco em interoperabilidade e apoio à Atenção Básica.
        </p>
      </section>

      {/* LISTAGEM */}
      <section id="listagem">
        <h2 className="text-2xl font-bold text-gray-700 mb-4">
          Listagem de Agendamentos
        </h2>

        <div className="grid md:grid-cols-1 gap-6">
          <section id="listagem">
            <InfoCard
              title="Agendamentos de Hoje"
              icon={Calendar}
            >
              <TabelaHoje />
            </InfoCard>
          </section>

        </div>
      </section>

      {/* ÁREA DE AGENDAMENTOS */}
      <section id="agendamentos">
        <h2 className="text-2xl font-bold text-gray-700 mb-4">
          Agendamentos
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <Card
            title="Agendar Consulta"
            description="Realizar um novo agendamento"
            icon={CalendarPlus}
            to="/agendamento"
          />

          <Card
            title="Gerenciar Agendamentos"
            description="Verificar dados de um agendamento"
            icon={Search}
            to="/agendamentos-crud"
          />
        </div>
      </section>

      {/* ÁREA DE CADASTROS */}
      <section id="cadastros">
        <h2 className="text-2xl font-bold text-gray-700 mb-4">
          Cadastros
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <Card
            title="Cadastro/Gerenciamento de Cidadão"
            description="Registrar cidadãos atendidos pela UBS"
            icon={UserPlus}
            to="/pacientes"
          />

          <Card
            title="Cadastro/Gerenciamento de Profissional da UBS"
            description="Registrar profissionais de saúde"
            icon={ClipboardList}
            to="/profissionais"
          />
        </div>
      </section>



    </div>
  );
}
