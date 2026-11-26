import { useState } from "react";
import { api } from "../../services/api";
import LineaTiempo from "../../components/LineaTiempo";

export default function ConsultaPublica() {
  const [codigo, setCodigo] = useState("");
  const [t, setT] = useState(null);
  const [error, setError] = useState("");

  async function buscar(e) {
    e.preventDefault();
    setError(""); setT(null);
    try { setT(await api.get(`/publico/tramite/${codigo.trim()}`)); }
    catch (err) { setError(err.message); }
  }

  return (
    <section className="tarjeta">
      <h2>Consultar trámite</h2>
      <form className="fila" onSubmit={buscar}>
        <input placeholder="Código de seguimiento" value={codigo}
               onChange={e => setCodigo(e.target.value)} required />
        <button>Consultar</button>
      </form>
      {error && <p className="error">{error}</p>}
      {t && (
        <>
          <p>
            <b>{t.tipo.replaceAll("_", " ")}</b> — estado: <b>{t.estado}</b> — atención
            estimada: {t.dias_estimados} días
          </p>
          <LineaTiempo historial={t.historial} />
        </>
      )}
    </section>
  );
}