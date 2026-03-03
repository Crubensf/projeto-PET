import { Outlet } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function AppShell() {
  return (
    <div className="min-h-screen flex flex-col bg-blue-50">
      
      {/* Header */}
      <Header />

      {/* Conteúdo das páginas */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
