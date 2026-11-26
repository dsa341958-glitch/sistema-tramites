import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../services/api";

export default function NuevoTramite() {
  const ir = useNavigate();
  const [tipos, setTipos] = useState([]);
  const [tipo, setTipo] = useState("");
  const [asunto, setAsunto] = useState("");
  const [vulnerable, setVulnerable] = useState(false);
  const [sugerido, setSugerido] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/publico/tipos").then(t => { setTipos(t); setTipo(t[0]?.nombre || ""); });
  }, []);

  async function sugerir() {
    if (asunto.trim().length < 5) return;
    try { setSugerido(await api.get(`/publico/sugerir-tipo?asunto=${encodeURIComponent(asunto)}`)); }
    catch { /* la sugerencia es opcional */ }
  }

  async function enviar(e) {
    e.preventDefault();
    setError("");
    try {
      const t = await api.post("/tramites", { tipo, asunto, vulnerable });
      ir(`/seguimiento/${t.codigo}`);
    } catch (err) { setError(err.message); }
  }

  const actual = tipos.find(t => t.nombre === tipo);

  return (
    <form className="tarjeta angosta" onSubmit={enviar}>
      <h2>Nuevo trámite</h2>
      <input placeholder="Asunto: describa su trámite" minLength={5} required
             value={asunto} onChange={e => setAsunto(e.target.value)} onBlur={sugerir} />
      {sugerido && sugerido.tipo !== tipo && (
        <p className="aviso">
          El sistema sugiere <b>{sugerido.tipo.replaceAll("_", " ")}</b> ({Math.round(sugerido.confianza * 100)} %){" "}
          <button type="button" className="chico" onClick={() => setTipo(sugerido.tipo)}>Usar</button>
        </p>
      )}
      <select value={tipo} onChange={e => setTipo(e.target.value)}>
        {tipos.map(t => <option key={t.nombre} value={t.nombre}>{t.nombre.replaceAll("_", " ")}</option>)}
      </select>
      {actual && (
        <p className="nota">
          Plazo legal: {actual.plazo_dias} días. Documentos: {actual.documentos_requeridos.join(", ")}.
        </p>
      )}
      <label className="check">
        <input type="checkbox" checked={vulnerable} onChange={e => setVulnerable(e.target.checked)} />
        <span>Soy adulto mayor, persona con discapacidad o gestante (el personal lo verificará)</span>
      </label>
      {error && <p className="error">{error}</p>}
      <button>Registrar trámite</button>
    </form>
  );
}