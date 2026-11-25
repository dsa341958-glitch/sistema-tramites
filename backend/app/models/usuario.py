from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from ..database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    dni = Column(String(12), unique=True, nullable=False)
    nombres = Column(String(120), nullable=False)
    email = Column(String(120))
    telefono = Column(String(20))
    password_hash = Column(String(100), nullable=False)
    rol = Column(String(12), nullable=False)          # ADMIN | CIUDADANO
    area_id = Column(Integer, ForeignKey("areas.id"))
    activo = Column(Boolean, default=True)
    creado = Column(DateTime, default=datetime.utcnow)

class Consentimiento(Base):
    __tablename__ = "consentimientos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    finalidad = Column(String(200), nullable=False)
    version = Column(String(10), default="1.0")
    aceptado = Column(Boolean, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)