import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../services/api";
import ConsentimientoModal from "../../components/ConsentimientoModal";

export default function Registro() {
  const ir = useNavigate();
  const [f, setF] = useState({ dni: "", nombres: "", email: "", telefono: "", password: "" });
  const [acepta, setAcepta] = useState(false);
  const [modal, setModal] = useState(false);
  const [error, setError] = useState("");
  const campo = (k) => ({ value: f[k], onChange: e => setF({ ...f, [k]: e.target.value }) });

  async function enviar(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/auth/registro", { ...f, email: f.email || null, consentimiento: acepta });
      alert("Registro exitoso. Ya puede ingresar.");
      ir("/login");
    } catch (err) { setError(err.message); }
  }

  return (
    <>
      <form className="tarjeta angosta" onSubmit={enviar}>
        <h2>Registro de ciudadano</h2>
        <input placeholder="DNI (8 dígitos)" maxLength={8} pattern="\d{8}" required {...campo("dni")} />
        <input placeholder="Nombres y apellidos" minLength={3} required {...campo("nombres")} />
        <input type="email" placeholder="Correo (opcional)" {...campo("email")} />
        <input placeholder="Celular (9 dígitos, empieza con 9)" maxLength={9} pattern="9\d{8}" required {...campo("telefono")} />
        <input type="password" placeholder="Contraseña (mínimo 8)" minLength={8} required {...campo("password")} />
        <label className="check">
          <input type="checkbox" checked={acepta} onChange={e => setAcepta(e.target.checked)} />
          <span>
            Acepto el tratamiento de mis datos personales.{" "}
            <a href="#" onClick={e => { e.preventDefault(); setModal(true); }}>Leer política</a>
          </span>
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={!acepta}>Registrarme</button>
      </form>
      {modal && (
        <ConsentimientoModal
          onAceptar={() => { setAcepta(true); setModal(false); }}
          onCerrar={() => setModal(false)}
        />
      )}
    </>
  );
}