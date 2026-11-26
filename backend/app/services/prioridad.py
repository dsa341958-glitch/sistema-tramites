import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Tramite, TipoTramite
from . import validacion

log = logging.getLogger("prioridad")
SEMAFORO = {"ALTA": "ROJO", "MEDIA": "AMARILLO", "BAJA": "VERDE"}
ORDEN = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
CERRADOS = ("FINALIZADO", "RECHAZADO")

def carga_area(db: Session, area_id: int) -> int:
    return (db.query(Tramite).join(TipoTramite)
            .filter(TipoTramite.area_id == area_id, Tramite.estado.not_in(CERRADOS)).count())

def _ml(tipo, vulnerable, antig_ratio, carga, faltantes):
    """Consulta los modelos; si fallan, el sistema sigue solo con reglas."""
    try:
        from ..ml import predecir
        return predecir.predecir(tipo, vulnerable, antig_ratio, carga, faltantes)
    except Exception as e:
        log.error("ML no disponible, se usan solo reglas: %s", e)
        return None

def calcular(tipo, vulnerable: bool, antiguedad_dias: int, carga: int, faltantes: float = 0.0):
    """60% reglas explicables + 40% modelo ML. Las reglas legales fijan un piso."""
    consumido = antiguedad_dias / tipo.plazo_dias
    reglas, motivos = 0.0, []
    if tipo.nombre == "salud_emergencia":
        reglas += 60; motivos.append("trámite de salud o emergencia")
    if vulnerable:
        reglas += 50; motivos.append("solicitante vulnerable (adulto mayor/discapacidad)")
    if consumido >= 0.8:
        reglas += 30; motivos.append("plazo legal por vencer")
    elif consumido >= 0.5:
        reglas += 15; motivos.append("más de la mitad del plazo consumido")
    if tipo.plazo_dias <= 5:
        reglas += 10; motivos.append("plazo legal corto")
    if carga > 20:
        reglas += 5; motivos.append("área con alta carga")
    reglas = min(reglas, 100.0)

    motivo = "; ".join(motivos) or "trámite regular"
    ml = _ml(tipo, vulnerable, consumido, carga, faltantes)
    if ml:
        puntaje = 0.6 * reglas + 0.4 * ml["prob_alta"] * 100
        motivo += f"; ML: {ml['prob_alta']:.0%} prob. alta"
    else:
        puntaje = reglas
    prioridad = "ALTA" if puntaje >= 50 else "MEDIA" if puntaje >= 20 else "BAJA"
    if tipo.nombre == "salud_emergencia" or vulnerable:
        prioridad = "ALTA"                  # piso legal: no depende del modelo
    return round(puntaje, 1), prioridad, motivo[:200]

def estimar_dias(tipo, carga: int, faltantes: float = 0.0) -> float:
    ml = _ml(tipo, False, 0.0, carga, faltantes)
    return ml["dias"] if ml else round(tipo.plazo_dias * 0.6 + carga * 0.15, 1)

def reevaluar(db: Session, t: Tramite):
    """Recalcula prioridad con la antigüedad real y marca expedientes atípicos."""
    antig = (datetime.utcnow() - t.creado).days
    carga = carga_area(db, t.tipo.area_id)
    faltantes = validacion.revisar(t)["prob_error"]
    t.puntaje, t.prioridad, t.motivo_prioridad = calcular(
        t.tipo, t.vulnerable, antig, carga, faltantes)
    ml = _ml(t.tipo, t.vulnerable, antig / t.tipo.plazo_dias, carga, faltantes)
    if ml:
        t.anomalia = ml["anomalia"]