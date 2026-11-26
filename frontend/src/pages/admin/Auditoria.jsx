import { useEffect, useState } from "react";
import { api, fechaLocal } from "../../services/api";

export default function Auditoria() {
  const [lista, setLista] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/admin/auditoria?limite=200").then(setLista).catch(e => setError(e.message));
  }, []);

  return (
    <section className="tarjeta">
      <h2>Bitácora de auditoría</h2>
      <p className="nota">Registro de las acciones realizadas en el sistema (Ley 29733 y transparencia).</p>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Entidad</th><th>Detalle</th><th>IP</th></tr>
        </thead>
        <tbody>
          {lista.map((r, i) => (
            <tr key={i}>
              <td>{fechaLocal(r.fecha)}</td><td>{r.usuario_id ?? "—"}</td><td>{r.accion}</td>
              <td>{r.entidad}</td><td>{r.detalle}</td><td>{r.ip}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}