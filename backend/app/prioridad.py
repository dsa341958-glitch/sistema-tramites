from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Tramite, TipoTramite

SEMAFORO = {"ALTA": "ROJO", "MEDIA": "AMARILLO", "BAJA": "VERDE"}
ORDEN = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
CERRADOS = ("FINALIZADO", "RECHAZADO")

def carga_area(db: Session, area_id: int) -> int:
    return (db.query(Tramite).join(TipoTramite)
            .filter(TipoTramite.area_id == area_id, Tramite.estado.not_in(CERRADOS)).count())

def calcular(tipo, vulnerable: bool, antiguedad_dias: int, carga: int):
    """Reglas explicables y auditables. En el paso 4 se combinan con el modelo ML."""
    puntaje, motivos = 0.0, []
    if tipo.nombre == "salud_emergencia":
        puntaje += 60; motivos.append("trámite de salud o emergencia")
    if vulnerable:
        puntaje += 50; motivos.append("solicitante vulnerable (adulto mayor/discapacidad)")
    consumido = antiguedad_dias / tipo.plazo_dias
    if consumido >= 0.8:
        puntaje += 30; motivos.append("plazo legal por vencer")
    elif consumido >= 0.5:
        puntaje += 15; motivos.append("más de la mitad del plazo consumido")
    if tipo.plazo_dias <= 5:
        puntaje += 10; motivos.append("plazo legal corto")
    if carga > 20:
        puntaje += 5; motivos.append("área con alta carga")
    puntaje = min(puntaje, 100.0)
    prioridad = "ALTA" if puntaje >= 50 else "MEDIA" if puntaje >= 20 else "BAJA"
    return puntaje, prioridad, ("; ".join(motivos) or "trámite regular")[:200]

def estimar_dias(tipo, carga: int) -> float:
    return round(tipo.plazo_dias * 0.6 + carga * 0.15, 1)

def reevaluar(db: Session, t: Tramite):
    antig = (datetime.utcnow() - t.creado).days
    t.puntaje, t.prioridad, t.motivo_prioridad = calcular(
        t.tipo, t.vulnerable, antig, carga_area(db, t.tipo.area_id))