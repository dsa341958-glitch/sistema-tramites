def revisar(t) -> dict:
    """Compara documentos requeridos vs presentados y estima el riesgo de error."""
    requeridos = [d.strip() for d in (t.tipo.documentos_requeridos or "").split(",") if d.strip()]
    presentados = {d.tipo_documento for d in t.documentos}
    faltantes = [d for d in requeridos if d not in presentados]
    prob = round(len(faltantes) / len(requeridos), 2) if requeridos else 0.0
    return {"requeridos": requeridos, "presentados": sorted(presentados),
            "faltantes": faltantes, "prob_error": prob}