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