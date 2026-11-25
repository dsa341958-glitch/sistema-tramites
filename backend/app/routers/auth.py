from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario, Consentimiento
from ..schemas.usuario import RegistroIn, TokenOut, UsuarioOut
from ..core.security import (hash_password, verificar_password, crear_token,
                             enmascarar_dni)
from ..core.deps import usuario_actual
from ..services import auditoria

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(d: RegistroIn, request: Request, db: Session = Depends(get_db)):
    if not d.consentimiento:
        raise HTTPException(400, "Debe aceptar el tratamiento de datos personales (Ley 29733)")
    if db.query(Usuario).filter_by(dni=d.dni).first():
        raise HTTPException(409, "El DNI ya está registrado")
    u = Usuario(dni=d.dni, nombres=d.nombres, email=d.email, telefono=d.telefono,
                password_hash=hash_password(d.password), rol="CIUDADANO")
    db.add(u)
    db.flush()
    db.add(Consentimiento(usuario_id=u.id, aceptado=True,
                          finalidad="Gestión de trámites municipales"))
    auditoria.registrar(db, u.id, "REGISTRO", "usuarios",
                        f"DNI {enmascarar_dni(d.dni)}", request.client.host)
    db.commit()
    db.refresh(u)
    return u

@router.post("/login", response_model=TokenOut)       # username = DNI
def login(request: Request, f: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    u = db.query(Usuario).filter_by(dni=f.username).first()
    if not u or not u.activo or not verificar_password(f.password, u.password_hash):
        auditoria.registrar(db, u.id if u else None, "LOGIN_FALLIDO", "usuarios",
                            f"DNI {enmascarar_dni(f.username)}", request.client.host)
        db.commit()
        raise HTTPException(401, "DNI o contraseña incorrectos")
    auditoria.registrar(db, u.id, "LOGIN", "usuarios", "", request.client.host)
    db.commit()
    return TokenOut(access_token=crear_token(u.id, u.rol),
                    usuario=UsuarioOut.model_validate(u))

@router.get("/yo", response_model=UsuarioOut)
def yo(u: Usuario = Depends(usuario_actual)):
    return u