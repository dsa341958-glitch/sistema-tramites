import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../services/api";

export default function Inicio() {
  const [k, setK] = useState(null);
  useEffect(() => { api.get("/publico/indicadores").then(setK).catch(() => {}); }, []);

  const items = k && [
    ["Trámites registrados", k.total],
    ["Finalizados", k.finalizados],
    ["Días promedio de atención", k.dias_promedio_atencion],
    ["Trámites observados (%)", k.tasa_observados_pct],
    ["Satisfacción (1 a 5)", k.satisfaccion_promedio ?? "—"],
  ];

  return (
    <>
      <section className="tarjeta">
        <h1>Trámites municipales en línea</h1>
        <p>Registre su trámite, adjunte sus documentos y reciba alertas sobre su estado.</p>
        <div className="botones">
          <Link className="boton" to="/registro">Registrarme</Link>
          <Link className="boton secundario" to="/consulta">Consultar un trámite</Link>
        </div>
      </section>
      {items && (
        <section className="tarjeta">
          <h2>Transparencia: indicadores públicos</h2>
          <div className="kpis">
            {items.map(([t, v]) => <div className="kpi" key={t}><b>{v}</b>{t}</div>)}
          </div>
        </section>
      )}
    </>
  );
}