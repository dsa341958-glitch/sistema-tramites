import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import RutaProtegida from "./routes/RutaProtegida";
import Inicio from "./pages/publico/Inicio";
import ConsultaPublica from "./pages/publico/ConsultaPublica";
import Login from "./pages/auth/Login";
import Registro from "./pages/auth/Registro";
import MisTramites from "./pages/usuario/MisTramites";
import NuevoTramite from "./pages/usuario/NuevoTramite";
import Seguimiento from "./pages/usuario/Seguimiento";
import Perfil from "./pages/usuario/Perfil";
import Dashboard from "./pages/admin/Dashboard";
import Tramites from "./pages/admin/Tramites";
import Usuarios from "./pages/admin/Usuarios";
import Configuracion from "./pages/admin/Configuracion";
import Auditoria from "./pages/admin/Auditoria";

const ciudadano = (el) => <RutaProtegida rol="CIUDADANO">{el}</RutaProtegida>;
const admin = (el) => <RutaProtegida rol="ADMIN">{el}</RutaProtegida>;

export default function App() {
  return (
    <>
      <Navbar />
      <main className="contenedor">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/consulta" element={<ConsultaPublica />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/mis-tramites" element={ciudadano(<MisTramites />)} />
          <Route path="/nuevo" element={ciudadano(<NuevoTramite />)} />
          <Route path="/seguimiento/:codigo" element={ciudadano(<Seguimiento />)} />
          <Route path="/perfil" element={ciudadano(<Perfil />)} />
          <Route path="/admin" element={admin(<Dashboard />)} />
          <Route path="/admin/tramites" element={admin(<Tramites />)} />
          <Route path="/admin/usuarios" element={admin(<Usuarios />)} />
          <Route path="/admin/configuracion" element={admin(<Configuracion />)} />
          <Route path="/admin/auditoria" element={admin(<Auditoria />)} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </>
  );
}