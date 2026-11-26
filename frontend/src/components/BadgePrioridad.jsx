const COLOR = { ALTA: "rojo", MEDIA: "amarillo", BAJA: "verde" };

export default function BadgePrioridad({ prioridad }) {
  return <span className={`badge ${COLOR[prioridad] || ""}`}>{prioridad}</span>;
}