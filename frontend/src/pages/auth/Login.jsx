import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const ir = useNavigate();
  const [dni, setDni] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function enviar(e) {
    e.preventDefault();
    setError("");
    try {
      const u = await login(dni, password);
      ir(u.rol === "ADMIN" ? "/admin" : "/mis-tramites");
    } catch (err) { setError(err.message); }
  }

  return (
    <form className="tarjeta angosta" onSubmit={enviar}>
      <h2>Ingresar</h2>
      <input placeholder="DNI" value={dni} onChange={e => setDni(e.target.value)} required />
      <input type="password" placeholder="Contraseña" value={password}
             onChange={e => setPassword(e.target.value)} required />
      {error && <p className="error">{error}</p>}
      <button>Ingresar</button>
      <p>¿No tiene cuenta? <Link to="/registro">Regístrese</Link></p>
    </form>
  );
}