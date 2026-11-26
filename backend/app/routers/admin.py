from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Tramite, TipoTramite, Area, Usuario, Historial, Auditoria
from ..core.deps import solo_admin
from ..core.security import hash_password, enmascarar_dni
from ..schemas.tramite import (TramiteOut, DetalleOut, CambioEstadoIn, TipoUpdateIn,
                               a_out, a_detalle)
from ..schemas.usuario import StaffIn
from ..services import auditoria, notificaciones, validacion, analitica, alertas
from ..services.prioridad import ORDEN, CERRADOS

router = APIRouter(prefix="/admin", tags=["Administración"])

def _tramite(db: Session, codigo: str) -> Tramite:
    t = db.query(Tramite).filter_by(codigo=codigo.upper()).first()
    if not t:
        raise HTTPException(404, "Trámite no encontrado")
    return t

# ---------- Trámites ----------
@router.get("/cola", response_model=list[TramiteOut])
def cola(estado: str | None = None, area_id: int | None = None,
         admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    q = db.query(Tramite).join(TipoTramite)
    q = q.filter(Tramite.estado == estado) if estado else q.filter(Tramite.estado.not_in(CERRADOS))
    if area_id:
        q = q.filter(TipoTramite.area_id == area_id)
    filas = sorted(q.all(), key=lambda t: (ORDEN[t.prioridad], -(t.puntaje or 0), t.creado))
    return [a_out(t, con_ciudadano=True) for t in filas[:100]]

@router.get("/tramites/{codigo}", response_model=DetalleOut)
def ver_tramite(codigo: str, admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return a_detalle(_tramite(db, codigo), con_ciudadano=True)

@router.patch("/tramites/{codigo}/estado", response_model=TramiteOut)
def cambiar_estado(codigo: str, d: CambioEstadoIn, request: Request,
                   admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    t = _tramite(db, codigo)
    if t.estado in CERRADOS:
        raise HTTPException(400, "El trámite ya está cerrado")
    if d.estado in ("OBSERVADO", "RECHAZADO") and not d.comentario.strip():
        raise HTTPException(400, "Indique el motivo")
    if d.estado == "FINALIZADO":
        faltan = validacion.revisar(t)["faltantes"]
        if faltan:
            raise HTTPException(400, f"No se puede finalizar: faltan documentos {faltan}")
    t.estado, t.responsable_id, t.actualizado = d.estado, admin.id, datetime.utcnow()
    if d.estado in CERRADOS:
        t.finalizado = datetime.utcnow()
    db.add(Historial(tramite_id=t.id, estado=d.estado, comentario=d.comentario,
                     usuario_id=admin.id))
    notificaciones.notificar(db, t, d.estado, motivo=d.comentario)
    auditoria.registrar(db, admin.id, "CAMBIAR_ESTADO", "tramites",
                        f"{t.codigo} -> {d.estado}", request.client.host)
    db.commit()
    return a_out(t, con_ciudadano=True)

# ---------- Usuarios ----------
@router.post("/usuarios", status_code=201)
def crear_usuario(d: StaffIn, request: Request, admin: Usuario = Depends(solo_admin),
                  db: Session = Depends(get_db)):
    if db.query(Usuario).filter_by(dni=d.dni).first():
        raise HTTPException(409, "El DNI ya existe")
    if not db.get(Area, d.area_id):
        raise HTTPException(400, "Área inexistente")
    u = Usuario(dni=d.dni, nombres=d.nombres, email=d.email, telefono=d.telefono,
                password_hash=hash_password(d.password), rol="ADMIN", area_id=d.area_id)
    db.add(u)
    db.flush()
    auditoria.registrar(db, admin.id, "CREAR_USUARIO", "usuarios",
                        f"{enmascarar_dni(d.dni)} (personal)", request.client.host)
    db.commit()
    return {"id": u.id}

@router.get("/usuarios")
def listar_usuarios(admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return [{"id": u.id, "dni": enmascarar_dni(u.dni), "nombres": u.nombres, "rol": u.rol,
             "area_id": u.area_id, "activo": u.activo}
            for u in db.query(Usuario).order_by(Usuario.id)]

@router.patch("/usuarios/{uid}/activo")
def activar(uid: int, activo: bool, request: Request,
            admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    u = db.get(Usuario, uid)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    if u.id == admin.id:
        raise HTTPException(400, "No puede desactivarse a sí mismo")
    u.activo = activo
    auditoria.registrar(db, admin.id, "ACTIVAR_USUARIO", "usuarios",
                        f"{enmascarar_dni(u.dni)} -> {activo}", request.client.host)
    db.commit()
    return {"id": u.id, "activo": u.activo}

# ---------- Configuración (flujos del TUPA) ----------
@router.get("/areas")
def areas(admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return [{"id": a.id, "nombre": a.nombre,
             "tipos": [{"id": t.id, "nombre": t.nombre, "plazo_dias": t.plazo_dias,
                        "documentos_requeridos": t.documentos_requeridos}
                       for t in db.query(TipoTramite).filter_by(area_id=a.id)]}
            for a in db.query(Area).order_by(Area.id)]

@router.patch("/tipos/{tipo_id}")
def editar_tipo(tipo_id: int, d: TipoUpdateIn, request: Request,
                admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    t = db.get(TipoTramite, tipo_id)
    if not t:
        raise HTTPException(404, "Tipo de trámite no encontrado")
    if d.plazo_dias is not None:
        t.plazo_dias = d.plazo_dias
    if d.documentos_requeridos is not None:
        t.documentos_requeridos = d.documentos_requeridos
    auditoria.registrar(db, admin.id, "EDITAR_TIPO", "tipos_tramite", t.nombre, request.client.host)
    db.commit()
    return {"id": t.id, "nombre": t.nombre, "plazo_dias": t.plazo_dias,
            "documentos_requeridos": t.documentos_requeridos}

# ---------- Analítica, alertas y auditoría ----------
@router.get("/dashboard")
def dashboard(admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return {"kpis": analitica.kpis(db), "por_estado": analitica.por_estado(db),
            "cuellos_de_botella": analitica.cuellos_de_botella(db)}

@router.post("/alertas/ejecutar")
def ejecutar_alertas(admin: Usuario = Depends(solo_admin)):
    """Corre ahora la revisión de vencimientos (útil para la demostración)."""
    return {"notificados": alertas.revisar_vencimientos()}

@router.get("/auditoria")
def ver_auditoria(limite: int = 100, admin: Usuario = Depends(solo_admin),
                  db: Session = Depends(get_db)):
    q = db.query(Auditoria).order_by(Auditoria.id.desc()).limit(min(limite, 500))
    return [{"fecha": r.fecha, "usuario_id": r.usuario_id, "accion": r.accion,
             "entidad": r.entidad, "detalle": r.detalle, "ip": r.ip} for r in q]


# ---------- Machine learning ----------
from ..models import ModeloML
from ..ml import entrenar as ml_entrenar, predecir as ml_predecir
from ..services import prioridad

@router.post("/reentrenar")
def reentrenar(request: Request, admin: Usuario = Depends(solo_admin),
               db: Session = Depends(get_db)):
    version, metricas = ml_entrenar.entrenar()
    for nombre, m in metricas.items():
        db.query(ModeloML).filter_by(nombre=nombre, activo=True).update({"activo": False})
        db.add(ModeloML(nombre=nombre, version=version, metricas=m,
                        ruta=ml_entrenar.ruta(nombre)))
    auditoria.registrar(db, admin.id, "REENTRENAR_ML", "modelos_ml", version, request.client.host)
    db.commit()
    ml_predecir.recargar()
    return {"version": version, "metricas": metricas}

@router.get("/modelos")
def modelos(admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    q = db.query(ModeloML).order_by(ModeloML.id.desc()).limit(20)
    return [{"nombre": m.nombre, "version": m.version, "metricas": m.metricas,
             "activo": m.activo, "entrenado": m.entrenado} for m in q]

@router.post("/reevaluar")
def reevaluar_todos(request: Request, admin: Usuario = Depends(solo_admin),
                    db: Session = Depends(get_db)):
    """Recalcula prioridad y anomalías de todos los trámites abiertos."""
    abiertos = db.query(Tramite).filter(Tramite.estado.not_in(CERRADOS)).all()
    for t in abiertos:
        prioridad.reevaluar(db, t)
    auditoria.registrar(db, admin.id, "REEVALUAR", "tramites", f"{len(abiertos)} trámites",
                        request.client.host)
    db.commit()
    return {"reevaluados": len(abiertos), "anomalias": sum(1 for t in abiertos if t.anomalia)}

@router.get("/anomalias", response_model=list[TramiteOut])
def anomalias(admin: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    q = db.query(Tramite).filter(Tramite.anomalia.is_(True), Tramite.estado.not_in(CERRADOS))
    return [a_out(t, con_ciudadano=True) for t in q]