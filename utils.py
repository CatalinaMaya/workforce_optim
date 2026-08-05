"""
utils.py
Funciones auxiliares: cálculo de métricas y exportación de resultados
a outputs/asignaciones.xlsx y outputs/resumen.xlsx (o a bytes en memoria
para descarga directa desde Streamlit).
"""

import io
import os
import pandas as pd
from openpyxl.styles import Font


def calcular_metricas(df_asignacion, df_resumen, n_colaboradores, n_dias, objetivo, tiempo):
    """Calcula las métricas resumen que se muestran en el dashboard."""
    total_asignado = len(df_asignacion)
    total_capacidad = n_colaboradores * n_dias
    utilizacion = (total_asignado / total_capacidad * 100) if total_capacidad else 0
    turnos_con_deficit = int((df_resumen["Déficit"] > 0).sum())
    turnos_con_exceso = int((df_resumen["Exceso"] > 0).sum())
    total_celdas = len(df_resumen)

    return {
        "total_asignado": total_asignado,
        "utilizacion": utilizacion,
        "objetivo": objetivo,
        "turnos_con_deficit": turnos_con_deficit,
        "turnos_con_exceso": turnos_con_exceso,
        "total_celdas": total_celdas,
        "tiempo": tiempo,
    }


def _formatear_hoja(writer, df, sheet_name):
    """Formato simple: fuente Arial, encabezado en negrita, ancho de columna ajustado."""
    ws = writer.sheets[sheet_name]
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(name="Arial", bold=True)
        max_len = max(df[col_name].astype(str).map(len).max() if len(df) else 0, len(col_name)) + 2
        ws.column_dimensions[cell.column_letter].width = max_len
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name="Arial")


def exportar_resultados(df_asignacion, df_resumen, output_dir="outputs"):
    """Guarda outputs/asignaciones.xlsx y outputs/resumen.xlsx en disco."""
    os.makedirs(output_dir, exist_ok=True)

    path_asignaciones = os.path.join(output_dir, "asignaciones.xlsx")
    with pd.ExcelWriter(path_asignaciones, engine="openpyxl") as writer:
        df_asignacion.to_excel(writer, sheet_name="Asignaciones", index=False)
        _formatear_hoja(writer, df_asignacion, "Asignaciones")

    path_resumen = os.path.join(output_dir, "resumen.xlsx")
    with pd.ExcelWriter(path_resumen, engine="openpyxl") as writer:
        df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
        _formatear_hoja(writer, df_resumen, "Resumen")

    return path_asignaciones, path_resumen


def to_excel_bytes(dict_dfs):
    """Convierte {nombre_hoja: df} a bytes de un .xlsx en memoria (para st.download_button)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nombre, df in dict_dfs.items():
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
            _formatear_hoja(writer, df, nombre[:31])
    return output.getvalue()