import { useEffect, useState } from "react";
import { api } from "../../services/api";
import TablaTramites from "../../components/TablaTramites";
import LineaTiempo from "../../components/LineaTiempo";

const ESTADOS = ["EN_REVISION", "OBSERVADO", "FINALIZADO", "RECHAZADO"];

export default function Tramites() {
  const [lista, setLista] = useState([]);
  const [estado, setEstado] = useState("");
  const [soloAnomalias, setSoloAnomalias] = useState(false);
  const [sel, setSel] = useState(null);
  const [nuevo, setNuevo] = useState("EN_REVISION");
  const [comentario, setComentario] = useState("");
  const [error, setError] = useState("");

  const cargar = () => {
    const ruta = soloAnomalias ? "/admin/anomalias" : `/admin/cola${estado ? `?estado=${estado}` : ""}`;
    api.get(ruta).then(setLista).catch(e => setError(e.message));
  };
  useEffect(() => { cargar(); }, [estado, soloAnomalias]);

  const ver = (c) => api.get(`/admin/tramites/${c}`).then(setSel).catch(e => setError(e.message));

  async function cambiar(e) {
    e.preventDefault();
    setError("");
    try {
      await api.patch(`/admin/tramites/${sel.codigo}/estado`, { estado: nuevo, comentario });
      setComentario(""); setSel(null); cargar();
    } catch (err) { setError(err.message); }
  }

  return (
    <>
      <section className="tarjeta">
        <h2>Cola de trámites (por prioridad)</h2>
        <div className="fila">
          <select value={estado} onChange={e => setEstado(e.target.value)} disabled={soloAnomalias}>
            <option value="">Abiertos</option>
            {["REGISTRADO", ...ESTADOS].map(s => <option key={s}>{s}</option>)}
          </select>
          <label className="check">
            <input type="checkbox" checked={soloAnomalias} onChange={e => setSoloAnomalias(e.target.checked)} />
            Solo anomalías detectadas por ML
          </label>
        </div>
        {error && <p className="error">{error}</p>}
        <TablaTramites tramites={lista} onVer={ver} verCiudadano />
      </section>

      {sel && (
        <section className="tarjeta">
          <h3>{sel.codigo} — {sel.tipo.replaceAll("_", " ")}</h3>
          <p>Ciudadano: {sel.ciudadano} · Asunto: {sel.asunto}</p>
          <p className="nota">{sel.motivo_prioridad}</p>
          <p>
            Documentos requeridos: {sel.documentos_requeridos.join(", ")}<br />
            Faltantes: <b>{sel.documentos_faltantes.join(", ") || "ninguno"}</b>
          </p>
          <LineaTiempo historial={sel.historial} />
          <form className="fila" onSubmit={cambiar}>
            <select value={nuevo} onChange={e => setNuevo(e.target.value)}>
              {ESTADOS.map(s => <option key={s}>{s}</option>)}
            </select>
            <input placeholder="Comentario (obligatorio si observa o rechaza)" value={comentario}
                   onChange={e => setComentario(e.target.value)} style={{ flex: 1 }} />
            <button>Aplicar</button>
            <button type="button" className="secundario" onClick={() => setSel(null)}>Cerrar</button>
          </form>
        </section>
      )}
    </>
  );
}