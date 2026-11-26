import { useEffect, useState } from "react";
import { api } from "../../services/api";

export default function Usuarios() {
  const [lista, setLista] = useState([]);
  const [areas, setAreas] = useState([]);
  const [f, setF] = useState({ dni: "", nombres: "", email: "", telefono: "", password: "", area_id: "" });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const campo = (k) => ({ value: f[k], onChange: e => setF({ ...f, [k]: e.target.value }) });

  const cargar = () => api.get("/admin/usuarios").then(setLista).catch(e => setError(e.message));
  useEffect(() => {
    cargar();
    api.get("/admin/areas").then(a => { setAreas(a); setF(x => ({ ...x, area_id: a[0]?.id ?? "" })); });
  }, []);

  async function crear(e) {
    e.preventDefault();
    setMsg(""); setError("");
    try {
      await api.post("/admin/usuarios", { ...f, email: f.email || null, area_id: +f.area_id });
      setMsg("Personal creado correctamente");
      setF({ ...f, dni: "", nombres: "", email: "", telefono: "", password: "" });
      cargar();
    } catch (err) { setError(err.message); }
  }

  async function alternar(u) {
    setError("");
    try { await api.patch(`/admin/usuarios/${u.id}/activo?activo=${!u.activo}`); cargar(); }
    catch (err) { setError(err.message); }
  }

  const nombreArea = (id) => areas.find(a => a.id === id)?.nombre ?? "—";

  return (
    <>
      <section className="tarjeta">
        <h2>Nuevo personal municipal</h2>
        <form className="fila" onSubmit={crear}>
          <input placeholder="DNI" maxLength={8} pattern="\d{8}" required {...campo("dni")} />
          <input placeholder="Nombres" minLength={3} required {...campo("nombres")} />
          <input type="email" placeholder="Correo" {...campo("email")} />
          <input placeholder="Celular" maxLength={9} pattern="9\d{8}" required {...campo("telefono")} />
          <input type="password" placeholder="Contraseña" minLength={8} required {...campo("password")} />
          <select {...campo("area_id")}>
            {areas.map(a => <option key={a.id} value={a.id}>{a.nombre}</option>)}
          </select>
          <button>Crear</button>
        </form>
        {msg && <p className="ok">{msg}</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <section className="tarjeta">
        <h2>Usuarios</h2>
        <table>
          <thead><tr><th>DNI</th><th>Nombres</th><th>Rol</th><th>Área</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            {lista.map(u => (
              <tr key={u.id}>
                <td>{u.dni}</td><td>{u.nombres}</td><td>{u.rol}</td><td>{nombreArea(u.area_id)}</td>
                <td>{u.activo ? "Activo" : "Inactivo"}</td>
                <td>
                  <button className="chico secundario" onClick={() => alternar(u)}>
                    {u.activo ? "Desactivar" : "Activar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}