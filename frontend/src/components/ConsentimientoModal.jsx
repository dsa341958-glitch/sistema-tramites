export default function ConsentimientoModal({ onAceptar, onCerrar }) {
  return (
    <div className="modal-fondo">
      <div className="modal">
        <h3>Tratamiento de datos personales (Ley N.° 29733)</h3>
        <p>
          La Municipalidad Provincial de Yau tratará sus datos personales únicamente para
          gestionar sus trámites y notificarle su estado.
        </p>
        <ul>
          <li>Solo se recogen los datos necesarios (minimización).</li>
          <li>Sus datos no se comparten con terceros sin su autorización.</li>
          <li>Puede ejercer sus derechos de acceso, rectificación, cancelación y oposición.</li>
          <li>Toda operación queda registrada en una bitácora de auditoría.</li>
        </ul>
        <div className="botones">
          <button onClick={onAceptar}>Acepto</button>
          <button className="secundario" onClick={onCerrar}>Cerrar</button>
        </div>
      </div>
    </div>
  );
}