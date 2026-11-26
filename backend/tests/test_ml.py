from types import SimpleNamespace
from app.ml import predecir
from app.services import prioridad

SALUD = SimpleNamespace(nombre="salud_emergencia", plazo_dias=2)
LICENCIA = SimpleNamespace(nombre="licencia_funcionamiento", plazo_dias=15)

def test_modelos_predicen():
    r = predecir.predecir(LICENCIA, False, 0.1, 5, 0.0)
    assert set(r) == {"prob_alta", "prioridad_ml", "dias", "anomalia"}
    assert r["dias"] > 0

def test_salud_vulnerable_tiene_probabilidad_alta():
    assert predecir.predecir(SALUD, True, 0.1, 5, 0.0)["prob_alta"] > 0.8

def test_tramite_regular_tiene_probabilidad_baja():
    assert predecir.predecir(LICENCIA, False, 0.1, 5, 0.0)["prob_alta"] < 0.3

def test_clasificador_sugiere_el_tipo():
    r = predecir.sugerir_tipo("quiero licencia para mi bodega")
    assert r["tipo"] == "licencia_funcionamiento" and r["confianza"] > 0.4

def test_piso_legal_salud_siempre_alta():
    _, prio, motivo = prioridad.calcular(SALUD, False, 0, 5)
    assert prio == "ALTA" and "salud" in motivo

def test_piso_legal_vulnerable_siempre_alta():
    assert prioridad.calcular(LICENCIA, True, 0, 5)[1] == "ALTA"

def test_plazo_consumido_sube_el_puntaje():
    nuevo = prioridad.calcular(LICENCIA, False, 0, 5)[0]
    viejo = prioridad.calcular(LICENCIA, False, 14, 5)[0]
    assert viejo >= nuevo