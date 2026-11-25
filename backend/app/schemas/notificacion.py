from datetime import datetime
from pydantic import BaseModel

class NotificacionOut(BaseModel):
    id: int
    tramite_id: int | None
    canal: str
    mensaje: str
    estado_envio: str
    fecha: datetime
    model_config = {"from_attributes": True}