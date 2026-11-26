import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { usuario, logout } = useAuth();
  const ir = useNavigate();
  const salir = () => { logout(); ir("/"); };

  return (
    <header className="navbar">
      <Link to="/" className="marca">Municipalidad Provincial de Yau</Link>
      <nav>
        <Link to="/consulta">Consultar trámite</Link>
        {usuario?.rol === "CIUDADANO" && (
          <>
            <Link to="/mis-tramites">Mis trámites</Link>
            <Link to="/nuevo">Nuevo trámite</Link>
            <Link to="/perfil">Perfil</Link>
          </>
        )}
        {usuario?.rol === "ADMIN" && (
          <>
            <Link to="/admin">Dashboard</Link>
            <Link to="/admin/tramites">Trámites</Link>
            <Link to="/admin/usuarios">Usuarios</Link>
            <Link to="/admin/configuracion">Configuración</Link>
            <Link to="/admin/auditoria">Auditoría</Link>
          </>
        )}
        {usuario ? (
          <button onClick={salir}>Salir</button>
        ) : (
          <>
            <Link to="/login">Ingresar</Link>
            <Link to="/registro">Registrarse</Link>
          </>
        )}
      </nav>
    </header>
  );
}