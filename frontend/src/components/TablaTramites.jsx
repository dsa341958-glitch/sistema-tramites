import BadgePrioridad from "./BadgePrioridad";

export default function TablaTramites({ tramites, onVer, verCiudadano = false }) {
  if (!tramites.length) return <p className="vacio">No hay trámites.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>Código</th><th>Tipo</th>
          {verCiudadano && <th>Ciudadano</th>}
          <th>Estado</th><th>Prioridad</th><th>Días est.</th><th></th>
        </tr>
      </thead>
      <tbody>
        {tramites.map(t => (
          <tr key={t.codigo}>
            <td>{t.codigo}</td>
            <td>{t.tipo.replaceAll("_", " ")}</td>
            {verCiudadano && <td>{t.ciudadano}</td>}
            <td>{t.estado}</td>
            <td><BadgePrioridad prioridad={t.prioridad} /></td>
            <td>{t.dias_estimados}</td>
            <td><button className="chico" onClick={() => onVer(t.codigo)}>Ver</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}