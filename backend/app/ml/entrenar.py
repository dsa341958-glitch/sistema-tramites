import os
from datetime import datetime
import joblib
from sklearn.ensemble import (GradientBoostingClassifier, GradientBoostingRegressor,
                              IsolationForest)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from .datos_sinteticos import generar, generar_textos, FEATURES

DIR = os.path.join(os.path.dirname(__file__), "modelos")
ARCHIVOS = {"prioridad": "prioridad.joblib", "tiempo": "tiempo.joblib",
            "clasificador": "clasificador.joblib", "anomalias": "anomalias.joblib"}
FEATURES_ANOMALIA = ["antig_ratio", "carga", "faltantes"]

def ruta(nombre: str) -> str:
    return os.path.join(DIR, ARCHIVOS[nombre])

def _guardar(nombre: str, modelo):
    joblib.dump(modelo, ruta(nombre))

def entrenar():
    """Entrena los 4 modelos, los guarda en disco y devuelve (versión, métricas)."""
    os.makedirs(DIR, exist_ok=True)
    df = generar()
    X, metricas = df[FEATURES], {}

    # 1. Prioridad (0 = BAJA, 1 = MEDIA, 2 = ALTA)
    Xa, Xb, ya, yb = train_test_split(X, df["prioridad"], test_size=.2,
                                      random_state=1, stratify=df["prioridad"])
    m = GradientBoostingClassifier(random_state=1).fit(Xa, ya)
    metricas["prioridad"] = {"f1_macro": round(float(f1_score(yb, m.predict(Xb), average="macro")), 3),
                             "muestras": int(len(df))}
    _guardar("prioridad", m)

    # 2. Tiempo de atención (días)
    Xa, Xb, ya, yb = train_test_split(X, df["dias"], test_size=.2, random_state=1)
    m = GradientBoostingRegressor(random_state=1).fit(Xa, ya)
    metricas["tiempo"] = {"mae_dias": round(float(mean_absolute_error(yb, m.predict(Xb))), 3)}
    _guardar("tiempo", m)

    # 3. Clasificador de tipo de trámite según el asunto
    textos, y = generar_textos()
    Ta, Tb, ya, yb = train_test_split(textos, y, test_size=.2, random_state=1)
    m = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)),
                      LogisticRegression(max_iter=500)).fit(Ta, ya)
    metricas["clasificador"] = {"accuracy": round(float(accuracy_score(yb, m.predict(Tb))), 3)}
    _guardar("clasificador", m)

    # 4. Anomalías (expedientes estancados o con carga atípica)
    m = IsolationForest(contamination=.03, random_state=1).fit(df[FEATURES_ANOMALIA])
    metricas["anomalias"] = {"contaminacion": 0.03}
    _guardar("anomalias", m)

    return datetime.utcnow().strftime("%Y%m%d%H%M%S"), metricas