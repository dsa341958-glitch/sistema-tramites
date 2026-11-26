import os
import joblib
import pandas as pd
from .datos_sinteticos import TIPOS, FEATURES
from .entrenar import ARCHIVOS, FEATURES_ANOMALIA, entrenar, ruta

NIVELES = {0: "BAJA", 1: "MEDIA", 2: "ALTA"}
_m = {}

def cargar():
    if not _m:
        if not all(os.path.exists(ruta(n)) for n in ARCHIVOS):
            entrenar()                      # primera vez: entrena con datos sintéticos
        for n in ARCHIVOS:
            _m[n] = joblib.load(ruta(n))
    return _m

def recargar():
    _m.clear()
    return cargar()

def predecir(tipo, vulnerable, antig_ratio, carga, faltantes=0.0) -> dict:
    m = cargar()
    idx = TIPOS.index(tipo.nombre) if tipo.nombre in TIPOS else 0
    fila = pd.DataFrame([[idx, tipo.plazo_dias, int(vulnerable), faltantes, carga, antig_ratio]],
                        columns=FEATURES)
    prob = dict(zip(m["prioridad"].classes_, m["prioridad"].predict_proba(fila)[0]))
    nivel = max(prob, key=prob.get)
    an = pd.DataFrame([[antig_ratio, carga, faltantes]], columns=FEATURES_ANOMALIA)
    return {"prob_alta": float(prob.get(2, 0.0)),
            "prioridad_ml": NIVELES[int(nivel)],
            "dias": round(float(m["tiempo"].predict(fila)[0]), 1),
            "anomalia": bool(m["anomalias"].predict(an)[0] == -1)}

def sugerir_tipo(asunto: str) -> dict:
    modelo = cargar()["clasificador"]
    p = modelo.predict_proba([asunto])[0]
    i = int(p.argmax())
    return {"tipo": TIPOS[int(modelo.classes_[i])], "confianza": round(float(p[i]), 2)}