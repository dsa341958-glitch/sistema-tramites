from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Tramite
from ..services import analitica

router = APIRouter(prefix="/publico", tags=["Público"])

@router.get("/tramite/{codigo}")
def consulta(codigo: str, db: Session = Depends(get_db)):
    t = db.query(Tramite).filter_by(codigo=codigo.upper()).first()
    if not t:
        raise HTTPException(404, "Código no encontrado")
    return {"codigo": t.codigo, "tipo": t.tipo.nombre, "estado": t.estado,
            "dias_estimados": t.dias_estimados,
            "historial": [{"estado": h.estado, "fecha": h.fecha} for h in t.historial]}

@router.get("/indicadores")
def indicadores(db: Session = Depends(get_db)):
    return analitica.kpis(db)


from ..ml import predecir

@router.get("/sugerir-tipo")
def sugerir_tipo(asunto: str):
    """Sugiere el tipo de trámite a partir del asunto escrito por el ciudadano."""
    return predecir.sugerir_tipo(asunto)


from ..models import TipoTramite

@router.get("/tipos")
def tipos(db: Session = Depends(get_db)):
    """Catálogo público de trámites (TUPA): plazo y documentos requeridos."""
    return [{"nombre": t.nombre, "plazo_dias": t.plazo_dias, "area": t.area.nombre,
             "documentos_requeridos": [d for d in t.documentos_requeridos.split(",") if d]}
            for t in db.query(TipoTramite).order_by(TipoTramite.id)]