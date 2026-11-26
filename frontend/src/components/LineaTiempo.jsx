import { fechaLocal } from "../services/api";

export default function LineaTiempo({ historial }) {
  return (
    <ol className="timeline">
      {historial.map((h, i) => (
        <li key={i}>
          <b>{h.estado}</b> <small>{fechaLocal(h.fecha)}</small>
          {h.comentario && <p>{h.comentario}</p>}
        </li>
      ))}
    </ol>
  );
}