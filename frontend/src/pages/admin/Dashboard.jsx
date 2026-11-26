import { useEffect, useState } from "react";
import { api } from "../../services/api";

export default function Dashboard() {
  const [d, setD] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const cargar = () => api.get("/admin/dashboard").then(setD).catch(e => setError(e.message));
  useEffect(() => { cargar(); }, []);

  async function accion(ruta, texto) {
    setMsg(""); setError("");
    try { setMsg(`${texto}: ${JSON.stringify(await api.post(ruta))}`); cargar(); }
    catch (e) { setError(e.message); }
  }

  if (!d) return <p className="error">{error || "Cargando..."}</p>;
  const k = d.kpis;
  const items = [
    ["Trámites", k.total], ["Finalizados", k.finalizados],
    ["Días promedio", k.dias_promedio_atencion], ["Observados (%)", k.tasa_observados_pct],
    ["Satisfacción", k.satisfaccion_promedio ?? "—"],
  ];

  return (
    <>
      <section className="tarjeta">
        <h2>Dashboard</h2>
        <div className="kpis">
          {items.map(([t, v]) => <div className="kpi" key={t}><b>{v}</b>{t}</div>)}
        </div>
        <p className="nota">
          Por estado: {Object.entries(d.por_estado).map(([e, n]) => `${e}: ${n}`).join(" · ") || "sin datos"}
        </p>
        <div className="botones">
          <button onClick={() => accion("/admin/reevaluar", "Reevaluados")}>Reevaluar prioridades (ML)</button>
          <button className="secundario" onClick={() => accion("/admin/alertas/ejecutar", "Alertas enviadas")}>
            Ejecutar alertas de vencimiento
          </button>
        </div>
        {msg && <p className="ok">{msg}</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <section className="tarjeta">
        <h3>Cuellos de botella por área</h3>
        {!d.cuellos_de_botella.length ? <p className="vacio">No hay trámites abiertos.</p> : (
          <table>
            <thead>
              <tr><th>Área</th><th>Abiertos</th><th>Vencidos</th><th>Antigüedad prom. (días)</th></tr>
            </thead>
            <tbody>
              {d.cuellos_de_botella.map(a => (
                <tr key={a.area}>
                  <td>{a.area}</td><td>{a.abiertos}</td><td>{a.vencidos}</td><td>{a.antiguedad_promedio_dias}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  );
}