from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from ..core.security import enmascarar_dni
from ..services.prioridad import SEMAFORO
from ..services import validacion

class TramiteIn(BaseModel):
    tipo: str
    asunto: str = Field(min_length=5, max_length=200)
    vulnerable: bool = False

class CambioEstadoIn(BaseModel):
    estado: Literal["EN_REVISION", "OBSERVADO", "FINALIZADO", "RECHAZADO"]
    comentario: str = Field(default="", max_length=300)

class EncuestaIn(BaseModel):
    calificacion: int = Field(ge=1, le=5)
    comentario: str = Field(default="", max_length=300)

class TipoUpdateIn(BaseModel):
    plazo_dias: int | None = Field(default=None, ge=1, le=365)
    documentos_requeridos: str | None = None

class HistorialOut(BaseModel):
    estado: str
    comentario: str | None = ""
    fecha: datetime
    model_config = {"from_attributes": True}

class TramiteOut(BaseModel):
    codigo: str
    tipo: str
    asunto: str | None = None
    estado: str
    prioridad: str
    semaforo: str
    motivo_prioridad: str | None = None
    prob_error: float | None = None
    dias_estimados: float | None = None
    ciudadano: str | None = None
    creado: datetime

class DetalleOut(TramiteOut):
    historial: list[HistorialOut]
    documentos_requeridos: list[str]
    documentos_faltantes: list[str]

def a_out(t, con_ciudadano: bool = False) -> TramiteOut:
    ciudadano = (f"{t.ciudadano.nombres} ({enmascarar_dni(t.ciudadano.dni)})"
                 if con_ciudadano else None)
    return TramiteOut(codigo=t.codigo, tipo=t.tipo.nombre, asunto=t.asunto, estado=t.estado,
                      prioridad=t.prioridad, semaforo=SEMAFORO[t.prioridad],
                      motivo_prioridad=t.motivo_prioridad, prob_error=t.prob_error,
                      dias_estimados=t.dias_estimados, ciudadano=ciudadano, creado=t.creado)

def a_detalle(t, con_ciudadano: bool = False) -> DetalleOut:
    r = validacion.revisar(t)
    return DetalleOut(**a_out(t, con_ciudadano).model_dump(),
                      historial=[HistorialOut.model_validate(h) for h in t.historial],
                      documentos_requeridos=r["requeridos"],
                      documentos_faltantes=r["faltantes"])