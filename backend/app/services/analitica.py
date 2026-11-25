from datetime import datetime
from sqlalchemy import func
from ..models import Tramite, Historial, Encuesta
from .prioridad import CERRADOS

def kpis(db) -> dict:
    total = db.query(func.count(Tramite.id)).scalar() or 0
    finalizados = db.query(func.count(Tramite.id)).filter(Tramite.estado == "FINALIZADO").scalar() or 0
    cerrados = db.query(Tramite.creado, Tramite.finalizado).filter(Tramite.finalizado.is_not(None)).all()
    dias = round(sum((f - c).total_seconds() for c, f in cerrados) / len(cerrados) / 86400, 1) if cerrados else 0
    observados = db.query(func.count(func.distinct(Historial.tramite_id))).filter(Historial.estado == "OBSERVADO").scalar() or 0
    satisfaccion = db.query(func.avg(Encuesta.calificacion)).scalar()
    return {"total": total, "finalizados": finalizados,
            "dias_promedio_atencion": dias,
            "tasa_observados_pct": round(100 * observados / total, 1) if total else 0,
            "satisfaccion_promedio": round(float(satisfaccion), 2) if satisfaccion else None}

def cuellos_de_botella(db) -> list:
    """Áreas ordenadas por trámites vencidos y abiertos."""
    ahora, por_area = datetime.utcnow(), {}
    for t in db.query(Tramite).filter(Tramite.estado.not_in(CERRADOS)).all():
        nombre = t.tipo.area.nombre
        a = por_area.setdefault(nombre, {"area": nombre, "abiertos": 0, "vencidos": 0, "_dias": 0})
        dias = (ahora - t.creado).days
        a["abiertos"] += 1
        a["_dias"] += dias
        if dias > t.tipo.plazo_dias:
            a["vencidos"] += 1
    res = []
    for a in por_area.values():
        a["antiguedad_promedio_dias"] = round(a.pop("_dias") / a["abiertos"], 1)
        res.append(a)
    return sorted(res, key=lambda x: (x["vencidos"], x["abiertos"]), reverse=True)

def por_estado(db) -> dict:
    return {e: n for e, n in db.query(Tramite.estado, func.count()).group_by(Tramite.estado).all()}