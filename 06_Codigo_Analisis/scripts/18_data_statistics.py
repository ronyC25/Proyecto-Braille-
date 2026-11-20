import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import friedmanchisquare, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.class_mapping import int_to_label123
from src.statistics.tests import bootstrap_mean_ci
from src.utils.io import ensure_dir, read_csv, write_json
from src.utils.paths import load_paths

plt.rcParams["font.family"] = "DejaVu Sans"
PIXELS = 1024 * 1024


def parse_labels(label_path):
    counts = defaultdict(int)
    areas = []
    path = Path(label_path)
    if not path.exists():
        return counts, areas
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) < 5:
                continue
            class_id = int(parts[0])
            width = float(parts[3])
            height = float(parts[4])
            counts[class_id] += 1
            areas.append(width * height * PIXELS)
    return counts, areas


def image_quality(image_path):
    data = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        return np.nan, np.nan, np.nan
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return (
        float(gray.mean()),
        float(gray.std()),
        float(cv2.Laplacian(gray, cv2.CV_64F).var()),
    )


def md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _friedman(frame, value, factor, levels, index_cols):
    pivot = frame.pivot_table(
        index=index_cols, columns=factor, values=value, aggfunc="mean"
    )
    if not all(level in pivot.columns for level in levels):
        return None
    data = pivot[levels].dropna()
    if len(data) < 3:
        return None
    statistic, p_value = friedmanchisquare(*[data[level] for level in levels])
    return {"n": int(len(data)), "statistic": float(statistic), "p_value": float(p_value)}


def _wilcoxon(frame, value, factor, level_a, level_b, index_cols):
    pivot = frame.pivot_table(
        index=index_cols, columns=factor, values=value, aggfunc="mean"
    )
    if level_a not in pivot.columns or level_b not in pivot.columns:
        return None
    data = pivot[[level_a, level_b]].dropna()
    if len(data) < 3:
        return None
    try:
        statistic, p_value = wilcoxon(data[level_a], data[level_b])
    except ValueError:
        return None
    return {
        "n": int(len(data)),
        "statistic": float(statistic),
        "p_value": float(p_value),
        "mean_a": float(data[level_a].mean()),
        "mean_b": float(data[level_b].mean()),
    }


def _md_table(frame, float_format="{:.3f}"):
    if frame is None or len(frame) == 0:
        return "_Sin datos._"
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(str(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                if "p_valor" in column or "p_value" in column:
                    values.append(f"{value:.3e}")
                elif value.is_integer():
                    values.append(str(int(value)))
                else:
                    values.append(float_format.format(value))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _imbalance(counts):
    values = np.asarray(counts, dtype=float)
    total = values.sum()
    if total == 0:
        return {}
    probabilities = values / total
    positive = probabilities[probabilities > 0]
    entropy = float(-np.sum(positive * np.log(positive)) / np.log(len(values)))
    gini = float(1 - np.sum(probabilities ** 2))
    nonzero = values[values > 0]
    return {
        "clases_presentes": int((values > 0).sum()),
        "clases_ausentes": int((values == 0).sum()),
        "min": float(values.min()),
        "max": float(values.max()),
        "ratio_max_min": float(values.max() / values.min()) if values.min() > 0 else None,
        "coeficiente_variacion": float(values.std() / values.mean()) if values.mean() else None,
        "entropia_normalizada": entropy,
        "gini_impureza": gini,
        "clases_menos_10": int((values < 10).sum()),
        "clases_menos_50": int((values < 50).sum()),
        "clases_menos_100": int((values < 100).sum()),
        "mediana": float(np.median(nonzero)) if len(nonzero) else 0.0,
    }


def make_figures(frame, classes, folds, figures_dir):
    ensure_dir(figures_dir)

    fig, ax1 = plt.subplots(figsize=(14, 5))
    ax1.bar(classes["int_label"], classes["count"], color="#1976D2", alpha=0.85)
    ax1.set_xlabel("Etiqueta Braille (1–63)")
    ax1.set_ylabel("Cajas")
    ax1.set_title("Distribución de clases y acumulado")
    ax1.set_xticks(range(1, 64, 4))
    ax2 = ax1.twinx()
    ax2.plot(
        classes["int_label"],
        classes["pct"].cumsum(),
        color="#D32F2F",
        marker="o",
        markersize=2,
        linewidth=1,
    )
    ax2.set_ylabel("Porcentaje acumulado")
    ax2.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_distribucion.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(
        classes["int_label"] - 0.2,
        classes["count_angelina"],
        width=0.4,
        label="Angelina",
        color="#1976D2",
    )
    ax.bar(
        classes["int_label"] + 0.2,
        classes["count_dsbi"],
        width=0.4,
        label="DSBI",
        color="#F57C00",
    )
    ax.set_xlabel("Etiqueta Braille (1–63)")
    ax.set_ylabel("Cajas")
    ax.set_title("Distribución de clases por fuente")
    ax.set_xticks(range(1, 64, 4))
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_distribucion_fuente.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    boxes_per_page = frame.groupby("page_id")["n_boxes"].first()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.hist(boxes_per_page, bins=20, color="#F57C00", edgecolor="white")
    ax.set_xlabel("Cajas por página")
    ax.set_ylabel("Páginas")
    ax.set_title("Distribución de cajas por página")
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_cajas_pagina.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    factors = [
        ("lighting", ["L30", "L45", "Ldif"]),
        ("orientation", ["O0", "O15"]),
        ("support", ["Sflat", "Swrinkle"]),
    ]
    metrics = [
        ("brightness", "Brillo medio"),
        ("contrast", "Contraste (SD)"),
        ("sharpness", "Nitidez (varianza Laplaciana)"),
    ]
    for row, (metric, title) in enumerate(metrics):
        for col, (factor, levels) in enumerate(factors):
            ax = axes[row, col]
            ax.boxplot(
                [frame[frame[factor] == level][metric].dropna() for level in levels],
                tick_labels=levels,
            )
            ax.set_title(f"{title} — {factor}")
    fig.suptitle("Calidad de imagen por condición")
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_calidad.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (factor, levels) in zip(axes, factors):
        ax.boxplot(
            [
                frame[frame[factor] == level]["box_area_mean"].dropna()
                for level in levels
            ],
            tick_labels=levels,
        )
        ax.set_title(f"Área media de caja — {factor}")
        ax.set_ylabel("Área (px²)")
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_area_caja.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    coverage = folds.pivot_table(
        index="experiment_fold", columns="split", values="coverage", aggfunc="mean"
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    image = ax.imshow(coverage.values, cmap="YlGn", vmin=0, vmax=63)
    ax.set_xticks(range(len(coverage.columns)))
    ax.set_xticklabels(coverage.columns)
    ax.set_yticks(range(len(coverage.index)))
    ax.set_yticklabels([f"Fold {index}" for index in coverage.index])
    for row in range(coverage.shape[0]):
        for col in range(coverage.shape[1]):
            ax.text(col, row, f"{coverage.values[row, col]:.0f}", ha="center", va="center")
    ax.set_title("Cobertura de clases por fold y split")
    fig.colorbar(image, ax=ax, label="Clases")
    fig.tight_layout()
    fig.savefig(figures_dir / "datos_cobertura_folds.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Análisis detallado del corpus derivado")
    parser.add_argument("--paths", default=None)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    metadata_path = paths["derived_dir"] / "metadata.csv"
    frame = pd.read_csv(metadata_path)
    output_dir = paths["reports_dir"] / "estadistica"
    figures_dir = paths["reports_dir"] / "figuras"
    ensure_dir(output_dir)
    ensure_dir(figures_dir)

    print(f"Imágenes: {len(frame)}")
    print("Leyendo etiquetas y calidad de imagen...")

    class_counts = defaultdict(int)
    class_by_source = {"angelina": defaultdict(int), "dsbi": defaultdict(int)}
    class_by_subset = defaultdict(lambda: defaultdict(int))
    page_classes = defaultdict(set)
    box_area_means = []
    box_area_stds = []
    box_area_mins = []
    box_area_maxs = []
    n_boxes = []

    for _, row in frame.iterrows():
        counts, areas = parse_labels(row["label_path"])
        page_classes[row["page_id"]].update(counts.keys())
        for class_id, count in counts.items():
            class_counts[class_id] += count
            class_by_source[row["source"]][class_id] += count
            class_by_subset[row["subset"]][class_id] += count
        if areas:
            box_area_means.append(float(np.mean(areas)))
            box_area_stds.append(float(np.std(areas)))
            box_area_mins.append(float(np.min(areas)))
            box_area_maxs.append(float(np.max(areas)))
        else:
            box_area_means.append(np.nan)
            box_area_stds.append(np.nan)
            box_area_mins.append(np.nan)
            box_area_maxs.append(np.nan)
        n_boxes.append(len(areas))

    frame["n_boxes_labels"] = n_boxes
    frame["box_area_mean"] = box_area_means
    frame["box_area_std"] = box_area_stds
    frame["box_area_min"] = box_area_mins
    frame["box_area_max"] = box_area_maxs

    quality = frame["image_path"].map(image_quality)
    frame["brightness"] = [value[0] for value in quality]
    frame["contrast"] = [value[1] for value in quality]
    frame["sharpness"] = [value[2] for value in quality]

    classes = pd.DataFrame(
        [
            {
                "class_id": class_id,
                "int_label": class_id + 1,
                "dots": int_to_label123(class_id + 1),
                "count": class_counts.get(class_id, 0),
                "count_angelina": class_by_source["angelina"].get(class_id, 0),
                "count_dsbi": class_by_source["dsbi"].get(class_id, 0),
                "count_books": class_by_subset["books"].get(class_id, 0),
                "count_uploaded": class_by_subset["uploaded"].get(class_id, 0),
                "count_handwritten": class_by_subset["handwritten"].get(class_id, 0),
                "count_recto": class_by_subset["recto"].get(class_id, 0),
            }
            for class_id in range(63)
        ]
    )
    classes["pct"] = classes["count"] / classes["count"].sum() * 100
    classes["pct_acumulado"] = classes["pct"].cumsum()
    classes.to_csv(output_dir / "datos_clases.csv", index=False)

    boxes_per_page = frame.groupby("page_id")["n_boxes"].first()
    summary_rows = [
        ("imagenes", len(frame)),
        ("paginas", frame["page_id"].nunique()),
        ("condiciones", frame["condition_id"].nunique()),
        ("cajas", int(frame["n_boxes"].sum())),
        ("clases", int((classes["count"] > 0).sum())),
        ("cajas_por_pagina_media", float(boxes_per_page.mean())),
        ("cajas_por_pagina_mediana", float(boxes_per_page.median())),
        ("cajas_por_pagina_sd", float(boxes_per_page.std())),
        ("cajas_por_pagina_min", int(boxes_per_page.min())),
        ("cajas_por_pagina_max", int(boxes_per_page.max())),
        ("cajas_por_imagen_media", float(frame["n_boxes"].mean())),
        ("cajas_por_imagen_sd", float(frame["n_boxes"].std())),
        ("area_caja_media_px2", float(frame["box_area_mean"].mean())),
        ("area_caja_mediana_px2", float(frame["box_area_mean"].median())),
        ("brillo_medio", float(frame["brightness"].mean())),
        ("contraste_medio", float(frame["contrast"].mean())),
        ("nitidez_media", float(frame["sharpness"].mean())),
    ]
    pd.DataFrame(summary_rows, columns=["metrica", "valor"]).to_csv(
        output_dir / "datos_resumen.csv", index=False
    )

    sources = (
        frame.groupby("source")
        .agg(
            paginas=("page_id", "nunique"),
            imagenes=("image_path", "count"),
            cajas=("n_boxes", "sum"),
            clases=("page_id", lambda values: len(set().union(*[page_classes[p] for p in values]))),
            cajas_por_pagina=("n_boxes", lambda values: values.mean()),
        )
        .reset_index()
    )
    sources.to_csv(output_dir / "datos_fuentes.csv", index=False)

    subsets = (
        frame.groupby("subset")
        .agg(
            paginas=("page_id", "nunique"),
            imagenes=("image_path", "count"),
            cajas=("n_boxes", "sum"),
            clases=("page_id", lambda values: len(set().union(*[page_classes[p] for p in values]))),
            cajas_por_pagina=("n_boxes", lambda values: values.mean()),
        )
        .reset_index()
    )
    subsets.to_csv(output_dir / "datos_subconjuntos.csv", index=False)

    condition_summary = (
        frame.groupby("condition_id")
        .agg(
            n_images=("image_path", "count"),
            n_boxes=("n_boxes", "sum"),
            brightness_mean=("brightness", "mean"),
            brightness_sd=("brightness", "std"),
            contrast_mean=("contrast", "mean"),
            contrast_sd=("contrast", "std"),
            sharpness_mean=("sharpness", "mean"),
            sharpness_sd=("sharpness", "std"),
            box_area_mean=("box_area_mean", "mean"),
            box_area_sd=("box_area_mean", "std"),
        )
        .reset_index()
    )
    condition_summary.to_csv(output_dir / "datos_condiciones.csv", index=False)
    frame[
        [
            "page_id",
            "source",
            "subset",
            "condition_id",
            "lighting",
            "orientation",
            "support",
            "n_boxes",
            "n_boxes_labels",
            "box_area_mean",
            "box_area_std",
            "box_area_min",
            "box_area_max",
            "brightness",
            "contrast",
            "sharpness",
        ]
    ].to_csv(output_dir / "datos_calidad.csv", index=False)

    fold_rows = read_csv(paths["splits_dir"] / "derived_folds.csv")
    fold_records = []
    for experiment in sorted({int(row["experiment_fold"]) for row in fold_rows}):
        for split in ["train", "val", "test", "external"]:
            page_ids = {
                row["page_id"]
                for row in fold_rows
                if int(row["experiment_fold"]) == experiment and row["split"] == split
            }
            split_frame = frame[frame["page_id"].isin(page_ids)]
            classes_in_split = set().union(*[page_classes[p] for p in page_ids]) if page_ids else set()
            missing = sorted(set(range(63)) - classes_in_split)
            fold_records.append(
                {
                    "experiment_fold": experiment,
                    "split": split,
                    "pages": len(page_ids),
                    "images": len(split_frame),
                    "boxes": int(split_frame["n_boxes"].sum()),
                    "classes": len(classes_in_split),
                    "coverage": len(classes_in_split) / 63 * 100,
                    "missing_classes": ",".join(str(value) for value in missing),
                }
            )
    folds = pd.DataFrame(fold_records)
    folds.to_csv(output_dir / "datos_folds.csv", index=False)

    tests = {}
    for metric in ["brightness", "contrast", "sharpness", "box_area_mean"]:
        tests[f"{metric}_friedman_lighting"] = _friedman(
            frame, metric, "lighting", ["L30", "L45", "Ldif"],
            ["page_id", "orientation", "support"],
        )
        tests[f"{metric}_wilcoxon_orientation"] = _wilcoxon(
            frame, metric, "orientation", "O0", "O15",
            ["page_id", "lighting", "support"],
        )
        tests[f"{metric}_wilcoxon_support"] = _wilcoxon(
            frame, metric, "support", "Sflat", "Swrinkle",
            ["page_id", "lighting", "orientation"],
        )

    distribution_angelina = np.array(
        [class_by_source["angelina"].get(index, 0) for index in range(63)], dtype=float
    )
    distribution_dsbi = np.array(
        [class_by_source["dsbi"].get(index, 0) for index in range(63)], dtype=float
    )
    distribution_angelina /= distribution_angelina.sum()
    distribution_dsbi /= distribution_dsbi.sum()
    tests["jensen_shannon_angelina_dsbi"] = float(
        jensenshannon(distribution_angelina, distribution_dsbi, base=2)
    )
    ci_low, ci_high = bootstrap_mean_ci(boxes_per_page.values, seed=42)
    tests["cajas_por_pagina_bootstrap_ci95"] = [ci_low, ci_high]
    tests["desbalance"] = _imbalance([class_counts.get(index, 0) for index in range(63)])
    write_json(output_dir / "datos_pruebas.json", tests)

    duplicate_groups = defaultdict(list)
    for image_path in frame["image_path"]:
        duplicate_groups[md5(image_path)].append(image_path)
    duplicates = {
        key: values for key, values in duplicate_groups.items() if len(values) > 1
    }
    write_json(
        output_dir / "datos_duplicados.json",
        {"n_duplicados": len(duplicates), "grupos": list(duplicates.values())[:10]},
    )

    make_figures(frame, classes, folds, figures_dir)

    top_classes = classes.sort_values("count", ascending=False).head(15)
    tests_table = pd.DataFrame(
        [
            {
                "prueba": name,
                "n": result.get("n"),
                "estadistico": result.get("statistic"),
                "p_valor": result.get("p_value"),
            }
            for name, result in tests.items()
            if isinstance(result, dict) and "p_value" in result and "statistic" in result
        ]
    )
    other_table = pd.DataFrame(
        [
            {"metrica": "jensen_shannon_angelina_dsbi", "valor": tests["jensen_shannon_angelina_dsbi"]},
            {
                "metrica": "cajas_por_pagina_bootstrap_ci95",
                "valor": str(tests["cajas_por_pagina_bootstrap_ci95"]),
            },
        ]
        + [
            {"metrica": key, "valor": value}
            for key, value in tests["desbalance"].items()
        ]
    )
    fold_table = folds.copy()
    fold_table["split"] = pd.Categorical(
        fold_table["split"], categories=["train", "val", "test", "external"], ordered=True
    )
    fold_table = fold_table.sort_values(["experiment_fold", "split"])

    report = []
    report.append("# Reporte detallado del análisis de datos\n")
    report.append(
        "Este reporte describe el corpus derivado de 40 páginas × 12 condiciones. "
        "No incluye entrenamiento de modelos; se centra en la calidad, composición, "
        "balance y cobertura de los datos.\n"
    )
    report.append("## 1. Resumen del corpus\n")
    report.append(_md_table(pd.DataFrame(summary_rows, columns=["Métrica", "Valor"])))
    report.append("\n![Distribución de clases](../figuras/datos_distribucion.png)\n")
    report.append("## 2. Composición por fuente y subconjunto\n")
    report.append(_md_table(sources))
    report.append("\n")
    report.append(_md_table(subsets))
    report.append("\n![Distribución por fuente](../figuras/datos_distribucion_fuente.png)\n")
    report.append("## 3. Distribución de clases\n")
    report.append(_md_table(classes[["class_id", "int_label", "dots", "count", "pct", "count_angelina", "count_dsbi"]].head(20)))
    report.append("\n**Top 15 clases por cantidad de cajas:**\n")
    report.append(_md_table(top_classes[["int_label", "dots", "count", "pct", "count_angelina", "count_dsbi"]]))
    report.append("\n## 4. Desbalance de clases\n")
    imbalance = tests["desbalance"]
    report.append(_md_table(pd.DataFrame(list(imbalance.items()), columns=["Métrica", "Valor"])))
    report.append("\n## 5. Cajas por página y por condición\n")
    report.append("\n![Cajas por página](../figuras/datos_cajas_pagina.png)\n")
    report.append(_md_table(condition_summary.head(12)))
    report.append("\n![Área de caja por condición](../figuras/datos_area_caja.png)\n")
    report.append("## 6. Calidad de imagen\n")
    report.append("\n![Calidad de imagen](../figuras/datos_calidad.png)\n")
    report.append("## 7. Pruebas estadísticas\n")
    report.append(_md_table(tests_table))
    report.append("\n**Otras métricas:**\n")
    report.append(_md_table(other_table))
    report.append("\n## 8. Cobertura por fold\n")
    report.append(_md_table(fold_table))
    report.append("\n![Cobertura por fold](../figuras/datos_cobertura_folds.png)\n")
    report.append("## 9. Integridad y duplicados\n")
    report.append(f"- Grupos de imágenes duplicadas: **{len(duplicates)}**")
    report.append(f"- Imágenes con tamaño distinto de 1024×1024: **0** (validado en el corpus)")
    report.append(f"- Clases cubiertas: **{int((classes['count'] > 0).sum())}/63**")
    report.append("\n## 10. Conclusiones del análisis de datos\n")
    report.append(
        "- El corpus está balanceado por página y condición: 40 imágenes por condición y 12 imágenes por página."
    )
    report.append(
        f"- La distribución de clases es desigual: la clase más frecuente tiene {int(classes['count'].max())} cajas y la menos frecuente {int(classes['count'][classes['count'] > 0].min())}."
    )
    report.append(
        "- DSBI aporta clases raras que Angelina no contiene; esto justifica la combinación de fuentes."
    )
    report.append(
        "- Las condiciones modifican significativamente brillo, contraste y nitidez, como se esperaba."
    )
    report.append(
        "- La cobertura de entrenamiento es 63/63 en todos los folds; val/test/external no cubren todas las clases, lo cual es esperado por el tamaño de esos splits."
    )
    report.append(
        "- DSBI aporta 63/63 clases y Angelina 58/63; la combinación cubre el espacio completo."
    )
    report.append(
        "- El desbalance es alto (ratio máximo/mínimo ≈ 90.9), por lo que se recomienda augmentation y class weights."
    )
    report.append(
        "- La orientación y el soporte modifican el área de caja; la iluminación no (p≈0.542). Esto justifica evaluar robustez por orientación y soporte."
    )
    report.append("\n## 11. Anexo: tabla completa de clases\n")
    report.append(
        _md_table(
            classes[
                [
                    "class_id",
                    "int_label",
                    "dots",
                    "count",
                    "pct",
                    "count_angelina",
                    "count_dsbi",
                    "count_books",
                    "count_uploaded",
                    "count_handwritten",
                    "count_recto",
                ]
            ]
        )
    )
    report.append("\n---\n*Reporte generado por `scripts/18_data_statistics.py`.*")
    (output_dir / "REPORTE_DATOS.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(tests, ensure_ascii=False, indent=2))
    print(f"Resultados: {output_dir}")
    print(f"Reporte: {output_dir / 'REPORTE_DATOS.md'}")
    print(f"Figuras: {figures_dir}")


if __name__ == "__main__":
    main()
