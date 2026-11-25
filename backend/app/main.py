from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import get_db
from .routers import auth, tramites, admin, notificaciones, publico
from .services import alertas

@asynccontextmanager
async def lifespan(app: FastAPI):
    alertas.iniciar()
    yield
    alertas.detener()

app = FastAPI(title="Sistema de Trámites - MP Yau", lifespan=lifespan)
for r in (auth, tramites, admin, notificaciones, publico):
    app.include_router(r.router)

@app.get("/salud")
def salud(db: Session = Depends(get_db)):
    tablas = db.execute(text(
        "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
    )).scalar()
    return {"api": "ok", "base_de_datos": "ok", "tablas": tablas}