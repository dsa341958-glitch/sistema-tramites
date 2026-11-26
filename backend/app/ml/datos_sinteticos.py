import numpy as np
import pandas as pd

TIPOS = ["licencia_funcionamiento", "certificado_posesion", "partida_nacimiento",
         "licencia_construccion", "salud_emergencia"]
PLAZOS = [15, 10, 5, 30, 2]
FEATURES = ["tipo_idx", "plazo_dias", "vulnerable", "faltantes", "carga", "antig_ratio"]

PALABRAS = {
    0: ["licencia", "funcionamiento", "bodega", "negocio", "apertura", "local comercial", "restaurante", "tienda"],
    1: ["certificado", "posesión", "terreno", "lote", "predio", "vivienda", "ubicación"],
    2: ["partida", "nacimiento", "acta", "registro civil", "hijo", "bebé", "copia certificada"],
    3: ["licencia", "construcción", "edificación", "obra", "planos", "ampliación", "casa"],
    4: ["emergencia", "salud", "urgente", "médica", "ambulancia", "atención", "enfermo"],
}
RELLENO = ["solicito", "para", "mi", "de", "necesito", "trámite", "por favor", "del", "una", "el"]

def generar(n: int = 3000, semilla: int = 42) -> pd.DataFrame:
    """Histórico sintético de trámites. En producción se reemplaza por datos reales."""
    rng = np.random.default_rng(semilla)
    tipo = rng.integers(0, len(TIPOS), n)
    plazo = np.array(PLAZOS)[tipo]
    vuln = (rng.random(n) < 0.15).astype(int)
    falt = rng.choice([0.0, 0.33, 0.5, 0.67, 1.0], n, p=[.45, .2, .15, .1, .1])
    carga = rng.integers(0, 45, n)
    ratio = rng.uniform(0, 1.1, n)                      # plazo consumido
    # La realidad no es una regla exacta: se agrega ruido
    p = (60 * (tipo == 4) + 50 * vuln + 30 * (ratio >= .8)
         + 15 * ((ratio >= .5) & (ratio < .8)) + 10 * (plazo <= 5)
         + 5 * (carga > 20) + rng.normal(0, 8, n))
    prioridad = np.where(p >= 50, 2, np.where(p >= 20, 1, 0))
    dias = np.clip(plazo * .6 + carga * .15 + falt * plazo * .4 + rng.normal(0, .8, n), .5, None)
    return pd.DataFrame({"tipo_idx": tipo, "plazo_dias": plazo, "vulnerable": vuln,
                         "faltantes": falt, "carga": carga, "antig_ratio": ratio,
                         "prioridad": prioridad, "dias": dias})

def generar_textos(n: int = 1500, semilla: int = 7):
    rng = np.random.default_rng(semilla)
    textos, etiquetas = [], []
    for _ in range(n):
        t = int(rng.integers(0, len(TIPOS)))
        palabras = ([str(x) for x in rng.choice(PALABRAS[t], int(rng.integers(2, 4)), replace=False)]
                    + [str(x) for x in rng.choice(RELLENO, int(rng.integers(1, 4)))])
        rng.shuffle(palabras)
        textos.append(" ".join(palabras))
        etiquetas.append(t)
    return textos, etiquetas