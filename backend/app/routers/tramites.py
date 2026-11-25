import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from ..config import UPLOAD_DIR
from ..database import get_db
from ..models import Tramite, TipoTramite, Historial, Documento, Encuesta, Usuario
from ..core.deps import solo_ciudadano
from ..schemas.tramite import TramiteIn, TramiteOut, DetalleOut, EncuestaIn, a_out, a_detalle
from ..services import auditoria, notificaciones, prioridad, validacion

router = APIRouter(prefix="/tramites", tags=["Trámites (ciudadano)"])
EXT_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_MB = 5

def _codigo(db: Session) -> str:
    while True:
        c = uuid.uuid4().hex[:8].upper()
        if not db.query(Tramite).filter_by(codigo=c).first():
            return c

def _propio(db: Session, u: Usuario, codigo: str) -> Tramite:
    t = db.query(Tramite).filter_by(codigo=codigo.upper(), ciudadano_id=u.id).first()
    if not t:
        raise HTTPException(404, "Trámite no encontrado")
    return t

@router.post("", response_model=TramiteOut, status_code=201)
def crear(d: TramiteIn, request: Request, u: Usuario = Depends(solo_ciudadano),
          db: Session = Depends(get_db)):
    tipo = db.query(TipoTramite).filter_by(nombre=d.tipo).first()
    if not tipo:
        raise HTTPException(400, "Tipo de trámite no válido")
    carga = prioridad.carga_area(db, tipo.area_id)
    puntaje, prio, motivo = prioridad.calcular(tipo, d.vulnerable, 0, carga)
    t = Tramite(codigo=_codigo(db), tipo_id=tipo.id, ciudadano_id=u.id, asunto=d.asunto,
                vulnerable=d.vulnerable, puntaje=puntaje, prioridad=prio,
                motivo_prioridad=motivo, dias_estimados=prioridad.estimar_dias(tipo, carga))
    db.add(t)
    db.flush()
    t.prob_error = validacion.revisar(t)["prob_error"]
    db.add(Historial(tramite_id=t.id, estado="REGISTRADO",
                     comentario="Trámite registrado", usuario_id=u.id))
    notificaciones.notificar(db, t, "REGISTRADO")
    auditoria.registrar(db, u.id, "CREAR_TRAMITE", "tramites", t.codigo, request.client.host)
    db.commit()
    return a_out(t)

@router.get("", response_model=list[TramiteOut])
def mis_tramites(u: Usuario = Depends(solo_ciudadano), db: Session = Depends(get_db)):
    q = db.query(Tramite).filter_by(ciudadano_id=u.id).order_by(Tramite.id.desc())
    return [a_out(t) for t in q]

@router.get("/{codigo}", response_model=DetalleOut)
def detalle(codigo: str, u: Usuario = Depends(solo_ciudadano), db: Session = Depends(get_db)):
    return a_detalle(_propio(db, u, codigo))

@router.post("/{codigo}/documentos", response_model=DetalleOut, status_code=201)
def adjuntar(codigo: str, request: Request, tipo_documento: str = Form(...),
             archivo: UploadFile = File(...), u: Usuario = Depends(solo_ciudadano),
             db: Session = Depends(get_db)):
    t = _propio(db, u, codigo)
    if t.estado in prioridad.CERRADOS:
        raise HTTPException(400, "El trámite ya está cerrado")
    pedidos = validacion.revisar(t)["requeridos"]
    if tipo_documento not in pedidos:
        raise HTTPException(400, f"Documento no solicitado. Válidos: {pedidos}")
    ext = os.path.splitext(archivo.filename or "")[1].lower()
    if ext not in EXT_PERMITIDAS:
        raise HTTPException(400, f"Formato no permitido. Use: {sorted(EXT_PERMITIDAS)}")
    contenido = archivo.file.read(MAX_MB * 1024 * 1024 + 1)
    if len(contenido) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"El archivo supera {MAX_MB} MB")

    carpeta = os.path.join(UPLOAD_DIR, t.codigo)
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{tipo_documento}_{uuid.uuid4().hex[:6]}{ext}")
    with open(ruta, "wb") as f:
        f.write(contenido)

    db.add(Documento(tramite_id=t.id, tipo_documento=tipo_documento,
                     nombre_original=(archivo.filename or "archivo")[:200], ruta=ruta))
    db.flush()
    db.refresh(t)
    r = validacion.revisar(t)
    t.prob_error = r["prob_error"]
    t.actualizado = datetime.utcnow()
    if t.estado == "OBSERVADO" and not r["faltantes"]:      # subsanación completa
        t.estado = "EN_REVISION"
        db.add(Historial(tramite_id=t.id, estado="EN_REVISION",
                         comentario="Subsanación presentada", usuario_id=u.id))
        notificaciones.notificar(db, t, "EN_REVISION")
    auditoria.registrar(db, u.id, "ADJUNTAR_DOCUMENTO", "documentos",
                        f"{t.codigo}:{tipo_documento}", request.client.host)
    db.commit()
    return a_detalle(t)

@router.post("/{codigo}/encuesta", status_code=201)
def encuesta(codigo: str, d: EncuestaIn, u: Usuario = Depends(solo_ciudadano),
             db: Session = Depends(get_db)):
    t = _propio(db, u, codigo)
    if t.estado != "FINALIZADO":
        raise HTTPException(400, "La encuesta se habilita cuando el trámite finaliza")
    if db.query(Encuesta).filter_by(tramite_id=t.id).first():
        raise HTTPException(409, "Ya calificó este trámite")
    db.add(Encuesta(tramite_id=t.id, calificacion=d.calificacion, comentario=d.comentario))
    db.commit()
    return {"mensaje": "Gracias por calificar el servicio"}