from sqlalchemy.orm import Session
from ..models import Auditoria

def registrar(db: Session, usuario_id, accion, entidad=None, detalle="", ip=None):
    """Agrega un registro a la bitácora. El commit lo hace quien llama."""
    db.add(Auditoria(usuario_id=usuario_id, accion=accion, entidad=entidad,
                     detalle=detalle[:300], ip=ip))