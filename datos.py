"""
datos.py
Generación de instancias sintéticas (A, R) y lectura/escritura desde/hacia
los archivos de datos en data/ (requerimiento.xlsx, disponibilidad.xlsx).
"""

import random
import pandas as pd
from openpyxl.styles import Font

TURNOS = ["Mañana", "Tarde", "Noche"]  # Fijos: modelo.py depende de estas etiquetas exactas
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# ------------------------------------------------------------------
# GENERACIÓN SINTÉTICA (equivalente a la instancia de prueba original)
# ------------------------------------------------------------------
def generar_instancia(colaboradores, dias, turnos, mercados, prob_disponibilidad, r_min, r_max, semilla):
    """Genera A (disponibilidad) y R (personal requerido) con random.seed(),
    replicando la lógica de la instancia de prueba original."""
    random.seed(semilla)

    A = {}
    for i in colaboradores:
        for d in dias:
            for t in turnos:
                A[(i, d, t)] = 1 if random.random() < prob_disponibilidad else 0

    R = {}
    for d in dias:
        for t in turnos:
            for m in mercados:
                R[(d, t, m)] = random.randint(r_min, r_max)

    return A, R


# ------------------------------------------------------------------
# CONVERSIÓN dict <-> DataFrame
# ------------------------------------------------------------------
def R_a_dataframe(R):
    return pd.DataFrame(
        [{"Día": d, "Turno": t, "Mercado": m, "Requerido": v} for (d, t, m), v in R.items()]
    )


def A_a_dataframe(A):
    return pd.DataFrame(
        [{"Colaborador": i, "Día": d, "Turno": t, "Disponible": v} for (i, d, t), v in A.items()]
    )


def dataframe_a_R(df):
    return {(row["Día"], row["Turno"], row["Mercado"]): int(row["Requerido"]) for _, row in df.iterrows()}


def dataframe_a_A(df):
    return {(row["Colaborador"], row["Día"], row["Turno"]): int(row["Disponible"]) for _, row in df.iterrows()}


# ------------------------------------------------------------------
# ESCRITURA A ARCHIVOS data/*.xlsx
# ------------------------------------------------------------------
def _formatear_encabezados(path_hoja_writer, df, sheet_name):
    """Aplica formato simple (fuente Arial, encabezado en negrita, ancho de columna)."""
    ws = path_hoja_writer.sheets[sheet_name]
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(name="Arial", bold=True)
        max_len = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 2
        ws.column_dimensions[cell.column_letter].width = max_len
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name="Arial")


def guardar_requerimiento(R, path="data/requerimiento.xlsx"):
    df = R_a_dataframe(R)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Requerimiento", index=False)
        _formatear_encabezados(writer, df, "Requerimiento")
    return path


def guardar_disponibilidad(A, path="data/disponibilidad.xlsx"):
    df = A_a_dataframe(A)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Disponibilidad", index=False)
        _formatear_encabezados(writer, df, "Disponibilidad")
    return path


# ------------------------------------------------------------------
# LECTURA DESDE ARCHIVOS data/*.xlsx
# ------------------------------------------------------------------
def cargar_requerimiento(path="data/requerimiento.xlsx"):
    df = pd.read_excel(path)
    return dataframe_a_R(df)


def cargar_disponibilidad(path="data/disponibilidad.xlsx"):
    df = pd.read_excel(path)
    return dataframe_a_A(df)