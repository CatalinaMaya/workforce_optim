"""
solver.py
Ejecuta el modelo (llama al solver) y extrae los resultados del modelo
ya resuelto en DataFrames.
"""

import time
import pandas as pd
from pyomo.environ import SolverFactory, value


def resolver_modelo(model, solver_name="appsi_highs"):
    """Resuelve el modelo con el solver indicado.

    Devuelve (result, tiempo_segundos).
    """
    solver = SolverFactory(solver_name)
    t0 = time.time()
    result = solver.solve(model)
    elapsed = time.time() - t0
    return result, elapsed


def extraer_resultados(model):
    """Extrae del modelo resuelto:
    - df_asignacion: detalle colaborador-día-turno-mercado asignado
    - df_resumen: cobertura por día-turno-mercado (requerido, asignado, exceso, déficit)
    """
    asignaciones = []
    for i in model.C:
        for d in model.D:
            for t in model.T:
                for m in model.M:
                    if value(model.x[i, d, t, m]) > 0.5:
                        asignaciones.append({
                            "Colaborador": i, "Día": d, "Turno": t, "Mercado": m
                        })
    df_asignacion = pd.DataFrame(asignaciones)

    resumen = []
    for d in model.D:
        for t in model.T:
            for m in model.M:
                asignado = sum(
                    1 for a in asignaciones
                    if a["Día"] == d and a["Turno"] == t and a["Mercado"] == m
                )
                requerido = model.R[d, t, m]
                exceso = value(model.e[d, t, m])
                deficit = value(model.f[d, t, m])
                resumen.append({
                    "Día": d, "Turno": t, "Mercado": m,
                    "Requerido": requerido, "Asignado": asignado,
                    "Exceso": round(exceso, 1), "Déficit": round(deficit, 1)
                })
    df_resumen = pd.DataFrame(resumen)

    return df_asignacion, df_resumen