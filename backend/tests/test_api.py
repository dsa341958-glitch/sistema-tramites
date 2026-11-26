import os
import random
import shutil
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import UPLOAD_DIR
from app.database import SessionLocal
from app.models import Usuario, Tramite
from app.services.prioridad import ORDEN

def _h(token):
    return {"Authorization": f"Bearer {token}"}

def _login(client, dni, password):
    return client.post("/auth/login", data={"username": dni, "password": password})

def _crear(client, h, tipo, asunto, vulnerable=False):
    r = client.post("/tramites", headers=h,
                    json={"tipo": tipo, "asunto": asunto, "vulnerable": vulnerable})
    assert r.status_code == 201, r.text
    return r.json()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def admin(client):
    r = _login(client, "00000000", os.getenv("ADMIN_PASSWORD", "Admin123!"))
    assert r.status_code == 200, "No se pudo entrar como administrador"
    return _h(r.json()["access_token"])

@pytest.fixture(scope="module")
def ciudadano(client):
    dni = "7" + "".join(random.choices("0123456789", k=7))
    r = client.post("/auth/registro", json={
        "dni": dni, "nombres": "Prueba Automática", "telefono": "987654321",
        "password": "Clave1234", "consentimiento": True})
    assert r.status_code == 201, r.text
    token = _login(client, dni, "Clave1234").json()["access_token"]
    yield {"dni": dni, "h": _h(token)}
    # Limpieza: borra lo creado por las pruebas
    db = SessionLocal()
    try:
        u = db.query(Usuario).filter_by(dni=dni).first()
        for t in db.query(Tramite).filter_by(ciudadano_id=u.id):
            shutil.rmtree(os.path.join(UPLOAD_DIR, t.codigo), ignore_errors=True)
        db.query(Tramite).filter_by(ciudadano_id=u.id).delete()
        db.delete(u)
        db.commit()
    finally:
        db.close()

@pytest.fixture(scope="module")
def licencia(client, ciudadano):
    return _crear(client, ciudadano["h"], "licencia_funcionamiento", "Licencia para bodega")

@pytest.fixture(scope="module")
def salud(client, ciudadano):
    return _crear(client, ciudadano["h"], "salud_emergencia", "Atención urgente", True)

# ---------- Acceso y seguridad ----------
def test_salud_api(client):
    r = client.get("/salud")
    assert r.status_code == 200 and r.json()["base_de_datos"] == "ok"

def test_registro_exige_consentimiento(client):
    r = client.post("/auth/registro", json={
        "dni": "71234567", "nombres": "Sin Consentimiento", "telefono": "987654321",
        "password": "Clave1234", "consentimiento": False})
    assert r.status_code == 400

def test_login_incorrecto(client):
    assert _login(client, "00000000", "clave-incorrecta").status_code == 401

def test_ruta_protegida_sin_token(client):
    assert client.get("/tramites").status_code == 401

def test_ciudadano_no_accede_a_admin(client, ciudadano):
    assert client.get("/admin/cola", headers=ciudadano["h"]).status_code == 403

# ---------- Priorización ----------
def test_salud_vulnerable_es_prioridad_alta(salud):
    assert salud["prioridad"] == "ALTA" and salud["semaforo"] == "ROJO"

def test_licencia_regular_es_prioridad_baja(licencia):
    assert licencia["prioridad"] == "BAJA"

def test_cola_ordenada_por_prioridad(client, admin, salud):
    cola = client.get("/admin/cola", headers=admin).json()
    ordenes = [ORDEN[t["prioridad"]] for t in cola]
    assert ordenes == sorted(ordenes)

# ---------- Reglas del flujo ----------
def test_observar_exige_motivo(client, admin, licencia):
    r = client.patch(f"/admin/tramites/{licencia['codigo']}/estado", headers=admin,
                     json={"estado": "OBSERVADO", "comentario": ""})
    assert r.status_code == 400

def test_no_se_finaliza_con_documentos_faltantes(client, admin, licencia):
    r = client.patch(f"/admin/tramites/{licencia['codigo']}/estado", headers=admin,
                     json={"estado": "FINALIZADO", "comentario": ""})
    assert r.status_code == 400

def test_rechaza_documento_no_solicitado(client, ciudadano, licencia):
    r = client.post(f"/tramites/{licencia['codigo']}/documentos", headers=ciudadano["h"],
                    data={"tipo_documento": "foto_mascota"},
                    files={"archivo": ("a.pdf", b"%PDF-1.4 prueba", "application/pdf")})
    assert r.status_code == 400

def test_adjuntar_documento_baja_el_riesgo(client, ciudadano, licencia):
    r = client.post(f"/tramites/{licencia['codigo']}/documentos", headers=ciudadano["h"],
                    data={"tipo_documento": "dni"},
                    files={"archivo": ("dni.pdf", b"%PDF-1.4 prueba", "application/pdf")})
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["prob_error"] < licencia["prob_error"]
    assert "dni" not in d["documentos_faltantes"]

# ---------- Protección de datos y transparencia ----------
def test_consulta_publica_no_expone_datos_personales(client, ciudadano, salud):
    r = client.get(f"/publico/tramite/{salud['codigo']}")
    assert r.status_code == 200
    assert "ciudadano" not in r.json()
    assert ciudadano["dni"] not in r.text

def test_listado_de_usuarios_enmascara_el_dni(client, admin, ciudadano):
    usuarios = client.get("/admin/usuarios", headers=admin).json()
    assert all("****" in u["dni"] for u in usuarios)
    assert ciudadano["dni"] not in [u["dni"] for u in usuarios]