from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    canal = Column(String(10), nullable=False)        # EMAIL | SMS | WHATSAPP
    mensaje = Column(String(300), nullable=False)
    estado_envio = Column(String(10), default="PENDIENTE")
    intentos = Column(Integer, default=0)
    fecha = Column(DateTime, default=datetime.utcnow)