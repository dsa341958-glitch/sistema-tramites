from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from ..database import SessionLocal
from ..models import Tramite, Notificacion
from . import notificaciones, prioridad

def revisar_vencimientos():
    """Cada hora: avisa de trámites a 2 días o menos de vencer y sube su prioridad."""
    db = SessionLocal()
    try:
        abiertos = db.query(Tramite).filter(Tramite.estado.not_in(prioridad.CERRADOS)).all()
        avisados = 0
        for t in abiertos:
            restan = t.tipo.plazo_dias - (datetime.utcnow() - t.creado).days
            if restan > 2:
                continue
            ya = db.query(Notificacion).filter(
                Notificacion.tramite_id == t.id,
                Notificacion.mensaje.like("%vence pronto%")).first()
            if not ya:
                prioridad.reevaluar(db, t)
                notificaciones.notificar(db, t, "POR_VENCER")
                avisados += 1
        db.commit()
        return avisados
    finally:
        db.close()

scheduler = BackgroundScheduler(timezone="America/Lima")

def iniciar():
    scheduler.add_job(revisar_vencimientos, "interval", hours=1,
                      id="vencimientos", replace_existing=True)
    scheduler.start()

def detener():
    scheduler.shutdown(wait=False)