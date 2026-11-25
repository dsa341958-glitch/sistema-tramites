from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Notificacion, Usuario
from ..core.deps import usuario_actual
from ..schemas.notificacion import NotificacionOut

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("", response_model=list[NotificacionOut])
def mias(u: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return (db.query(Notificacion).filter_by(usuario_id=u.id)
            .order_by(Notificacion.id.desc()).limit(30).all())