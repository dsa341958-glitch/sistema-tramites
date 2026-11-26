const BASE = import.meta.env.VITE_API_URL || "/api";

async function pedir(ruta, { metodo = "GET", cuerpo, form } = {}) {
  const headers = {};
  const token = localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;
  let body;
  if (form) body = form;                    // login (urlencoded) o archivos
  else if (cuerpo !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(cuerpo);
  }
  const r = await fetch(BASE + ruta, { method: metodo, headers, body });
  const datos = await r.json().catch(() => null);
  if (!r.ok) {
    if (r.status === 401 && token) {        // sesión vencida
      localStorage.clear();
      window.location.href = "/login";
    }
    const d = datos?.detail;
    throw new Error(typeof d === "string" ? d
      : Array.isArray(d) ? d.map(e => e.msg).join(". ") : "Error del servidor");
  }
  return datos;
}

export const api = {
  get: (r) => pedir(r),
  post: (r, cuerpo) => pedir(r, { metodo: "POST", cuerpo }),
  patch: (r, cuerpo) => pedir(r, { metodo: "PATCH", cuerpo }),
  form: (r, form) => pedir(r, { metodo: "POST", form }),
};

// El servidor guarda fechas en UTC sin zona: se les agrega "Z" para mostrar hora local
export const fechaLocal = (s) =>
  s ? new Date(/Z|[+-]\d\d:\d\d$/.test(s) ? s : s + "Z").toLocaleString("es-PE") : "";