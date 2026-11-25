from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Boolean, DateTime, Text,
                        ForeignKey)
from sqlalchemy.orm import relationship
from ..database import Base

class Area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)

class TipoTramite(Base):
    __tablename__ = "tipos_tramite"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    plazo_dias = Column(Integer, nullable=False)
    documentos_requeridos = Column(Text, default="")
    area = relationship("Area")

class Tramite(Base):
    __tablename__ = "tramites"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(12), unique=True, nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_tramite.id"), nullable=False)
    ciudadano_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    responsable_id = Column(Integer, ForeignKey("usuarios.id"))
    asunto = Column(String(200))
    estado = Column(String(12), default="REGISTRADO")
    prioridad = Column(String(5), default="MEDIA")
    puntaje = Column(Float)
    motivo_prioridad = Column(String(200))
    prob_error = Column(Float)
    dias_estimados = Column(Float)
    vulnerable = Column(Boolean, default=False)
    anomalia = Column(Boolean, default=False)
    creado = Column(DateTime, default=datetime.utcnow)
    actualizado = Column(DateTime, default=datetime.utcnow)
    finalizado = Column(DateTime)
    tipo = relationship("TipoTramite")
    ciudadano = relationship("Usuario", foreign_keys=[ciudadano_id])
    historial = relationship("Historial", order_by="Historial.id")
    documentos = relationship("Documento")

class Historial(Base):
    __tablename__ = "historial"
    id = Column(Integer, primary_key=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=False)
    estado = Column(String(12), nullable=False)
    comentario = Column(String(300), default="")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(DateTime, default=datetime.utcnow)

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=False)
    tipo_documento = Column(String(60), nullable=False)
    nombre_original = Column(String(200), nullable=False)
    ruta = Column(String(300), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

class Encuesta(Base):
    __tablename__ = "encuestas"
    id = Column(Integer, primary_key=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"), unique=True, nullable=False)
    calificacion = Column(Integer, nullable=False)
    comentario = Column(String(300), default="")
    fecha = Column(DateTime, default=datetime.utcnow)