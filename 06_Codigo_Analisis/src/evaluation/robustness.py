"""Robustez: evaluación en las 12 condiciones del corpus derivado.

TODO: agrupar métricas por lighting/orientation/support y calcular ΔmAP y ΔCER
respecto de la condición de referencia L30_O0_Sflat.
"""


def summarize_by_condition(metrics_rows):
    groups = {}
    for row in metrics_rows:
        key = (row["lighting"], row["orientation"], row["support"])
        groups.setdefault(key, []).append(row)
    return groups
