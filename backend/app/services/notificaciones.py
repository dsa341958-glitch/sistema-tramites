import logging
from ..models import Notificacion

log = logging.getLogger("notificaciones")
MAX_INTENTOS = 3

MENSAJES = {
    "REGISTRADO": "Su trámite {c} fue registrado. Prioridad {p}. Atención estimada en {d} días.",
    "EN_REVISION": "Su trámite {c} está en revisión.",
    "OBSERVADO": "Su trámite {c} tiene observaciones: {m}. Subsane a la brevedad.",
    "FINALIZADO": "Su trámite {c} fue finalizado. Califique la atención recibida.",
    "RECHAZADO": "Su trámite {c} fue rechazado. Motivo: {m}.",
    "POR_VENCER": "Aviso: el plazo de su trámite {c} vence pronto.",
}

def _enviar(canal: str, destino: str, mensaje: str) -> bool:
    """Punto de integración: aquí se conectan SMTP, API de SMS y WhatsApp Business."""
    log.warning("[%s -> %s***] %s", canal, destino[:3], mensaje)
    return True

def _entregar(db, t, usuario, canal, destino, mensaje) -> bool:
    n = Notificacion(tramite_id=t.id, usuario_id=usuario.id, canal=canal, mensaje=mensaje[:300])
    db.add(n)
    for intento in range(1, MAX_INTENTOS + 1):          # reintentos
        n.intentos = intento
        if _enviar(canal, destino, mensaje):
            n.estado_envio = "ENVIADO"
            return True
    n.estado_envio = "FALLIDO"
    return False

def notificar(db, t, evento: str, motivo: str = "") -> str:
    u = t.ciudadano
    msg = MENSAJES[evento].format(c=t.codigo, p=t.prioridad,
                                  d=round(t.dias_estimados or 0), m=motivo)
    if u.telefono and not _entregar(db, t, u, "WHATSAPP", u.telefono, msg):
        _entregar(db, t, u, "SMS", u.telefono, msg)      # respaldo si falla WhatsApp
    if u.email:
        _entregar(db, t, u, "EMAIL", u.email, msg)
    return msg