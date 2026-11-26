import { useEffect, useState } from "react";
import { api, fechaLocal } from "../../services/api";

export default function Configuracion() {
  const [areas, setAreas] = useState([]);
  const [modelos, setModelos] = useState([]);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const cargar = () => {
    api.get("/admin/areas").then(setAreas).catch(e => setError(e.message));
    api.get("/admin/modelos").then(setModelos).catch(() => {});
  };
  useEffect(() => { cargar(); }, []);

  const editar = (id, campo, valor) => setAreas(areas.map(a => ({
    ...a, tipos: a.tipos.map(t => (t.id === id ? { ...t, [campo]: valor } : t)),
  })));

  async function guardar(t) {
    setMsg(""); setError("");
    try {
      await api.patch(`/admin/tipos/${t.id}`,
        { plazo_dias: +t.plazo_dias, documentos_requeridos: t.documentos_requeridos });
      setMsg(`Guardado: ${t.nombre}`);
    } catch (e) { setError(e.message); }
  }

  async function reentrenar() {
    setMsg("Entrenando modelos..."); setError("");
    try {
      const r = await api.post("/admin/reentrenar");
      setMsg(`Modelos reentrenados (versión ${r.version})`);
      cargar();
    } catch (e) { setMsg(""); setError(e.message); }
  }

  return (
    <>
      <section className="tarjeta">
        <h2>Flujos de trámites (TUPA)</h2>
        <p className="nota">Documentos requeridos separados por coma, sin espacios.</p>
        <table>
          <thead>
            <tr><th>Área</th><th>Trámite</th><th>Plazo (días)</th><th>Documentos requeridos</th><th></th></tr>
          </thead>
          <tbody>
            {areas.flatMap(a => a.tipos.map(t => (
              <tr key={t.id}>
                <td>{a.nombre}</td>
                <td>{t.nombre}</td>
                <td>
                  <input type="number" min="1" style={{ width: 70 }} value={t.plazo_dias}
                         onChange={e => editar(t.id, "plazo_dias", e.target.value)} />
                </td>
                <td>
                  <input style={{ width: "100%" }} value={t.documentos_requeridos}
                         onChange={e => editar(t.id, "documentos_requeridos", e.target.value)} />
                </td>
                <td><button className="chico" onClick={() => guardar(t)}>Guardar</button></td>
              </tr>
            )))}
          </tbody>
        </table>
        {msg && <p className="ok">{msg}</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <section className="tarjeta">
        <h2>Modelos de machine learning</h2>
        <button onClick={reentrenar}>Reentrenar modelos</button>
        <table>
          <thead><tr><th>Modelo</th><th>Versión</th><th>Métricas</th><th>Activo</th><th>Entrenado</th></tr></thead>
          <tbody>
            {modelos.map((m, i) => (
              <tr key={i}>
                <td>{m.nombre}</td><td>{m.version}</td><td>{JSON.stringify(m.metricas)}</td>
                <td>{m.activo ? "Sí" : "No"}</td><td>{fechaLocal(m.entrenado)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}