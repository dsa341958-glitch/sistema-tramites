import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../../services/api";
import BadgePrioridad from "../../components/BadgePrioridad";
import LineaTiempo from "../../components/LineaTiempo";

const CERRADOS = ["FINALIZADO", "RECHAZADO"];

export default function Seguimiento() {
  const { codigo } = useParams();
  const [t, setT] = useState(null);
  const [doc, setDoc] = useState("");
  const [archivo, setArchivo] = useState(null);
  const [nota, setNota] = useState(5);
  const [comentario, setComentario] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const cargar = () => api.get(`/tramites/${codigo}`)
    .then(d => { setT(d); setDoc(d.documentos_faltantes[0] || ""); })
    .catch(e => setError(e.message));
  useEffect(() => { cargar(); }, [codigo]);

  async function subir(e) {
    e.preventDefault();
    const formulario = e.target;
    setMsg(""); setError("");
    const datos = new FormData();
    datos.append("tipo_documento", doc);
    datos.append("archivo", archivo);
    try {
      await api.form(`/tramites/${codigo}/documentos`, datos);
      setMsg("Documento adjuntado correctamente");
      formulario.reset();
      setArchivo(null);
      cargar();
    } catch (err) { setError(err.message); }
  }

  async function calificar(e) {
    e.preventDefault();
    setMsg(""); setError("");
    try {
      const r = await api.post(`/tramites/${codigo}/encuesta`, { calificacion: +nota, comentario });
      setMsg(r.mensaje);
    } catch (err) { setError(err.message); }
  }

  if (!t) return <p className="error">{error || "Cargando..."}</p>;
  const abierto = !CERRADOS.includes(t.estado);

  return (
    <section className="tarjeta">
      <p><Link to="/mis-tramites">← Mis trámites</Link></p>
      <h2>Trámite {t.codigo}</h2>
      <p>
        {t.tipo.replaceAll("_", " ")} — <b>{t.estado}</b> <BadgePrioridad prioridad={t.prioridad} />
      </p>
      <p className="nota">{t.motivo_prioridad}</p>
      <p>
        Atención estimada: <b>{t.dias_estimados} días</b> · Riesgo de observación:{" "}
        <b>{Math.round((t.prob_error || 0) * 100)} %</b>
      </p>
      {msg && <p className="ok">{msg}</p>}
      {error && <p className="error">{error}</p>}

      {abierto && t.documentos_faltantes.length > 0 && (
        <form onSubmit={subir} className="fila">
          <b>Documentos faltantes:</b>
          <select value={doc} onChange={e => setDoc(e.target.value)}>
            {t.documentos_faltantes.map(d => <option key={d}>{d}</option>)}
          </select>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" required
                 onChange={e => setArchivo(e.target.files[0])} />
          <button>Adjuntar</button>
        </form>
      )}

      <h3>Historial</h3>
      <LineaTiempo historial={t.historial} />

      {t.estado === "FINALIZADO" && (
        <form onSubmit={calificar} className="fila">
          <b>Califique la atención:</b>
          <select value={nota} onChange={e => setNota(e.target.value)}>
            {[5, 4, 3, 2, 1].map(n => <option key={n}>{n}</option>)}
          </select>
          <input placeholder="Comentario (opcional)" value={comentario}
                 onChange={e => setComentario(e.target.value)} />
          <button>Enviar</button>
        </form>
      )}
    </section>
  );
}