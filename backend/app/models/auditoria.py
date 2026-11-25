from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base

class Auditoria(Base):
    __tablename__ = "auditoria"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer)
    accion = Column(String(60), nullable=False)
    entidad = Column(String(60))
    detalle = Column(String(300), default="")
    ip = Column(String(45))
    fecha = Column(DateTime, default=datetime.utcnow)

class ModeloML(Base):
    __tablename__ = "modelos_ml"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(60), nullable=False)
    version = Column(String(20), nullable=False)
    metricas = Column(JSONB)
    ruta = Column(String(300))
    activo = Column(Boolean, default=True)
    entrenado = Column(DateTime, default=datetime.utcnow)