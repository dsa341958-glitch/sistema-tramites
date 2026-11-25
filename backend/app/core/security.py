from datetime import datetime, timedelta, timezone
import bcrypt, jwt
from ..config import SECRET_KEY, TOKEN_HORAS

def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verificar_password(p: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode(), hash_guardado.encode())
    except ValueError:
        return False

def crear_token(usuario_id: int, rol: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HORAS)
    return jwt.encode({"sub": str(usuario_id), "rol": rol, "exp": exp},
                      SECRET_KEY, algorithm="HS256")

def decodificar_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def enmascarar_dni(dni: str) -> str:      # 12345678 -> 12****78
    return dni[:2] + "****" + dni[-2:] if len(dni) >= 6 else "****"