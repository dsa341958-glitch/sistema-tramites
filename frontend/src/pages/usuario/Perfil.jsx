import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { api, fechaLocal } from "../../services/api";

export default function Perfil() {
  const { usuario } = useAuth();
  const [lista, setLista] = useState([]);

  useEffect(() => { api.get("/notificaciones").then(setLista).catch(() => {}); }, []);

  return (
    <section className="tarjeta">
      <h2>Mi perfil</h2>
      <p><b>{usuario.nombres}</b> — DNI {usuario.dni}</p>
      <h3>Mis notificaciones</h3>
      {!lista.length ? <p className="vacio">Aún no tiene notificaciones.</p> : (
        <table>
          <thead><tr><th>Fecha</th><th>Canal</th><th>Mensaje</th><th>Envío</th></tr></thead>
          <tbody>
            {lista.map(n => (
              <tr key={n.id}>
                <td>{fechaLocal(n.fecha)}</td><td>{n.canal}</td><td>{n.mensaje}</td><td>{n.estado_envio}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}