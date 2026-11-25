from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario
from .security import decodificar_token

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/login")

def usuario_actual(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> Usuario:
    try:
        datos = decodificar_token(token)
    except PyJWTError:
        raise HTTPException(401, "Token inválido o vencido")
    u = db.get(Usuario, int(datos["sub"]))
    if not u or not u.activo:
        raise HTTPException(401, "Usuario inactivo o inexistente")
    return u

def solo_admin(u: Usuario = Depends(usuario_actual)) -> Usuario:
    if u.rol != "ADMIN":
        raise HTTPException(403, "Solo para administradores")
    return u

def solo_ciudadano(u: Usuario = Depends(usuario_actual)) -> Usuario:
    if u.rol != "CIUDADANO":
        raise HTTPException(403, "Solo para ciudadanos")
    return u