import { createContext, useContext, useState } from "react";
import { api } from "../services/api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => {
    try { return JSON.parse(localStorage.getItem("usuario")); } catch { return null; }
  });

  async function login(dni, password) {
    const d = await api.form("/auth/login", new URLSearchParams({ username: dni, password }));
    localStorage.setItem("token", d.access_token);
    localStorage.setItem("usuario", JSON.stringify(d.usuario));
    setUsuario(d.usuario);
    return d.usuario;
  }

  function logout() {
    localStorage.clear();
    setUsuario(null);
  }

  return <Ctx.Provider value={{ usuario, login, logout }}>{children}</Ctx.Provider>;
}