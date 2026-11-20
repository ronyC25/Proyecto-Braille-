import argparse
import math
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.photometric import apply_condition, letterbox
from src.utils.io import read_csv, read_json
from src.utils.paths import load_paths

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 200

FIG_DIR = None


def _save(fig, name, overwrite=True):
    path = FIG_DIR / name
    if path.exists() and not overwrite:
        print(f"  existe, se omite: {name}")
        plt.close(fig)
        return path
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  guardado: {path}")
    return path


def _flow_box(ax, x, y, width, height, text, color="#E3F2FD", fontsize=9):
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=1.2,
        edgecolor="#37474F",
        facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#102027",
    )


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#37474F", lw=1.4),
    )


def figure_pipeline_general():
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Pipeline general del análisis", fontsize=15, pad=12)

    w, h = 0.17, 0.11
    y1, y2 = 0.70, 0.34
    xs = [0.02, 0.21, 0.40, 0.59, 0.78]
    row1 = ["Angelina", "DSBI +recto", "Auditoría", "Catálogo 40", "Corpus 480"]
    row2 = ["YOLO + folds", "Entrenamiento", "Evaluación", "ONNX / INT8", "App"]
    colors1 = ["#E8F5E9", "#E8F5E9", "#FFF3E0", "#FFF3E0", "#E3F2FD"]
    colors2 = ["#E3F2FD", "#F3E5F5", "#F3E5F5", "#FFEBEE", "#E0F7FA"]
    for x, text, color in zip(xs, row1, colors1):
        _flow_box(ax, x, y1, w, h, text, color)
    for x, text, color in zip(xs, row2, colors2):
        _flow_box(ax, x, y2, w, h, text, color)

    _arrow(ax, 0.19, y1 + h / 2, 0.40, y1 + h / 2)
    _arrow(ax, 0.38, y1 + h / 2, 0.40, y1 + h / 2)
    _arrow(ax, 0.57, y1 + h / 2, 0.59, y1 + h / 2)
    _arrow(ax, 0.76, y1 + h / 2, 0.78, y1 + h / 2)
    _arrow(ax, 0.865, y1, 0.865, y2 + h)
    for index in range(4):
        _arrow(ax, xs[index] + w, y2 + h / 2, xs[index + 1], y2 + h / 2)

    ax.text(
        0.5,
        0.12,
        "Los datos crudos no se copian: el pipeline lee Angelina y DSBI desde "
        "configs/paths.yaml.",
        ha="center",
        fontsize=9,
        color="#455A64",
    )
    return _save(fig, "pipeline_general.png")


def figure_pipeline_imagen():
    fig, ax = plt.subplots(figsize=(16, 3.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Pipeline de procesamiento de una imagen", fontsize=14, pad=10)
    labels = [
        "Original",
        "Letterbox\n1024×1024",
        "Orientación\nO0 / O15",
        "Iluminación\nL30 / L45 / Ldif",
        "Soporte\nSflat / Swrinkle",
        "Recorte\nde cajas",
        "JPEG 95\n+ etiquetas",
    ]
    colors = ["#ECEFF1", "#E3F2FD", "#E8F5E9", "#FFF3E0", "#F3E5F5", "#FFEBEE", "#E0F7FA"]
    width = 0.115
    gap = 0.017
    for index, (label, color) in enumerate(zip(labels, colors)):
        x = 0.02 + index * (width + gap)
        _flow_box(ax, x, 0.36, width, 0.30, label, color, fontsize=8.5)
        if index < len(labels) - 1:
            _arrow(ax, x + width, 0.51, x + width + gap, 0.51)
    return _save(fig, "pipeline_imagen.png")


def _load_sample(paths):
    catalog = read_csv(paths["splits_dir"] / "page_catalog.csv")
    page_id = catalog[0]["page_id"]
    page = read_json(paths["interim_dir"] / "pages" / f"{page_id}.json")
    image = Image.open(page["image_path"]).convert("RGB")
    boxes = [
        (box["x1"], box["y1"], box["x2"], box["y2"], box["class_id"])
        for box in page["boxes"]
    ]
    return page_id, image, boxes


def _draw_boxes(ax, boxes, color="#D32F2F", linewidth=0.8, alpha=0.75, highlight=None):
    for index, (x1, y1, x2, y2, _class_id) in enumerate(boxes):
        edge = color if highlight is None or index == highlight else "#1976D2"
        lw = linewidth + (1.2 if highlight is not None and index == highlight else 0)
        ax.add_patch(
            Rectangle(
                (x1, y1),
                max(1, x2 - x1),
                max(1, y2 - y1),
                fill=False,
                edgecolor=edge,
                linewidth=lw,
                alpha=alpha,
            )
        )


def figure_letterbox(paths, page_id, image, boxes):
    width, height = image.size
    canvas, transformed = letterbox(image, boxes, size=1024)
    scale = min(1024 / width, 1024 / height)
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    pad_x = (1024 - new_width) // 2
    pad_y = (1024 - new_height) // 2

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].imshow(image)
    _draw_boxes(axes[0], boxes, highlight=0)
    axes[0].set_title(f"Original {width}×{height}")
    axes[0].axis("off")

    axes[1].imshow(canvas)
    _draw_boxes(axes[1], transformed, highlight=0)
    axes[1].set_title("Letterbox 1024×1024")
    axes[1].axis("off")

    fig.suptitle(
        f"Letterbox — escala={scale:.4f}, pad_x={pad_x}, pad_y={pad_y}",
        fontsize=12,
    )
    fig.tight_layout()
    return _save(fig, "letterbox.png")


def figure_orientacion():
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Orientación O15: homografía de 15°", fontsize=13)

    source = np.array([[0.10, 0.20], [0.90, 0.20], [0.90, 0.80], [0.10, 0.80]])
    destination = np.array([[0.20, 0.20], [0.80, 0.20], [0.90, 0.80], [0.10, 0.80]])
    ax.add_patch(
        plt.Polygon(source, closed=True, fill=False, edgecolor="#1976D2", linestyle="--", lw=2)
    )
    ax.add_patch(
        plt.Polygon(destination, closed=True, fill=False, edgecolor="#D32F2F", lw=2)
    )
    for point in source:
        ax.plot(point[0], point[1], "o", color="#1976D2")
    for point in destination:
        ax.plot(point[0], point[1], "o", color="#D32F2F")
    for start, end in zip(source, destination):
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops=dict(arrowstyle="->", color="#616161", lw=1),
        )
    ax.text(0.50, 0.14, "Origen", ha="center", color="#1976D2", fontsize=11)
    ax.text(0.50, 0.87, "Destino (15°)", ha="center", color="#D32F2F", fontsize=11)
    ax.text(0.18, 0.22, "10%", color="#D32F2F", fontsize=9)
    ax.text(0.78, 0.22, "90%", color="#D32F2F", fontsize=9)
    ax.text(0.50, 0.18, "2%", color="#D32F2F", fontsize=9)
    ax.text(
        0.5,
        0.03,
        "Esquema no a escala. Las esquinas se transforman con cv2.perspectiveTransform.",
        ha="center",
        fontsize=8,
        color="#455A64",
    )
    return _save(fig, "orientacion.png")


def figure_iluminacion(paths, page_id):
    conditions = ["L30_O0_Sflat", "L45_O0_Sflat", "Ldif_O0_Sflat"]
    titles = ["L30 (rasante 30°)", "L45 (rasante 45°)", "Ldif (difusa)"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, condition, title in zip(axes, conditions, titles):
        path = paths["derived_dir"] / "images" / f"{page_id}__{condition}.jpg"
        ax.imshow(Image.open(path).convert("RGB"))
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle("Iluminación: misma página, O0, Sflat", fontsize=13)
    fig.tight_layout()
    return _save(fig, "iluminacion.png")


def figure_arrugas(paths, page_id):
    flat = paths["derived_dir"] / "images" / f"{page_id}__L30_O0_Sflat.jpg"
    wrinkle = paths["derived_dir"] / "images" / f"{page_id}__L30_O0_Swrinkle.jpg"
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(Image.open(flat).convert("RGB"))
    axes[0].set_title("Sflat (hoja lisa)")
    axes[0].axis("off")
    axes[1].imshow(Image.open(wrinkle).convert("RGB"))
    axes[1].set_title("Swrinkle (arrugas)")
    axes[1].axis("off")

    x = np.linspace(0, 1, 14)
    y = np.linspace(0, 1, 14)
    xx, yy = np.meshgrid(x, y)
    phase = 0.7
    amplitude = 0.02
    u = amplitude * np.sin(4 * math.pi * yy + phase)
    v = amplitude * np.sin(4 * math.pi * xx + phase)
    axes[2].quiver(xx, yy, u, v, color="#7B1FA2")
    axes[2].set_title("Campo de desplazamiento (ilustrativo)")
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].set_aspect("equal")
    fig.suptitle("Soporte: deformación elástica + sombra de pliegue", fontsize=13)
    fig.tight_layout()
    return _save(fig, "arrugas.png")


def figure_cajas(paths, page_id, image, boxes):
    selected = max(boxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]))
    letterboxed, letterbox_boxes = letterbox(image, [selected], size=1024)
    oriented, oriented_boxes, _ = apply_condition(
        image, [selected], "L30", "O15", "Sflat", seed=123
    )
    wrinkled, wrinkled_boxes, _ = apply_condition(
        image, [selected], "L30", "O0", "Swrinkle", seed=123
    )

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    panels = [
        (image, [selected], "Original"),
        (letterboxed, letterbox_boxes, "Letterbox"),
        (oriented, oriented_boxes, "O15"),
        (wrinkled, wrinkled_boxes, "Swrinkle"),
    ]
    for ax, (panel_image, panel_boxes, title) in zip(axes, panels):
        ax.imshow(panel_image)
        _draw_boxes(ax, panel_boxes, color="#D32F2F", highlight=0)
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle("Transformación de una caja a través del pipeline", fontsize=13)
    fig.tight_layout()
    return _save(fig, "cajas_transformadas.png")


def figure_folds(paths):
    rows = read_csv(paths["splits_dir"] / "derived_folds.csv")
    by_fold = {}
    for row in rows:
        fold = int(row["experiment_fold"])
        by_fold.setdefault(fold, {}).setdefault(row["split"], set()).add(row["page_id"])
    folds = sorted(by_fold)
    labels = [f"Fold {fold}" for fold in folds] + ["Externo"]
    train = [len(by_fold[fold].get("train", set())) for fold in folds]
    val = [len(by_fold[fold].get("val", set())) for fold in folds]
    test = [len(by_fold[fold].get("test", set())) for fold in folds]
    external = [len(by_fold[fold].get("external", set())) for fold in folds]

    fig, ax = plt.subplots(figsize=(12, 5))
    y = np.arange(len(folds))
    ax.barh(y, train, color="#1976D2", label="Train")
    ax.barh(y, val, left=train, color="#F57C00", label="Val")
    ax.barh(y, test, left=np.array(train) + np.array(val), color="#D32F2F", label="Test")
    external_row = len(folds)
    ax.barh(external_row, external[0], color="#607D8B", label="Externo")
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Páginas")
    ax.set_title("Distribución de páginas por fold")
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.28))
    for index, (t, v, te) in enumerate(zip(train, val, test)):
        ax.text(t / 2, index, str(t), va="center", ha="center", color="white", fontsize=9)
        ax.text(t + v / 2, index, str(v), va="center", ha="center", color="white", fontsize=9)
        ax.text(t + v + te / 2, index, str(te), va="center", ha="center", color="white", fontsize=9)
    ax.text(external[0] / 2, external_row, str(external[0]), va="center", ha="center", color="white")
    fig.tight_layout()
    return _save(fig, "folds.png")


def figure_mapeo_clases():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Mapeo de una celda Braille a class_id", fontsize=13)

    dots = [1, 0, 0, 1, 1, 0]
    positions = [(0.18, 0.72), (0.18, 0.50), (0.18, 0.28), (0.32, 0.72), (0.32, 0.50), (0.32, 0.28)]
    for index, ((x, y), dot) in enumerate(zip(positions, dots), start=1):
        ax.add_patch(plt.Circle((x, y), 0.035, color="#D32F2F" if dot else "#CFD8DC"))
        ax.text(x, y, str(index), ha="center", va="center", color="white" if dot else "#37474F", fontsize=9)
    ax.text(0.25, 0.10, "Puntos 1, 4 y 5", ha="center", fontsize=10)

    ax.text(0.48, 0.72, f"Binario: {dots}", fontsize=11)
    ax.text(0.48, 0.56, "int_label = 1 + 8 + 16 = 25", fontsize=11)
    ax.text(0.48, 0.40, "class_id = 25 - 1 = 24", fontsize=11)
    ax.text(0.48, 0.24, "YOLO: clase 24", fontsize=11, color="#D32F2F")
    ax.text(
        0.48,
        0.08,
        "Fórmula: int_label = Σ 2^(punto-1)",
        fontsize=9,
        color="#455A64",
    )
    return _save(fig, "mapeo_clases.png")


def main():
    parser = argparse.ArgumentParser(description="Genera figuras del pipeline")
    parser.add_argument("--paths", default=None)
    parser.add_argument("--page-id", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    global FIG_DIR
    paths = load_paths(args.paths)
    FIG_DIR = paths["reports_dir"] / "figuras"
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    page_id, image, boxes = _load_sample(paths)
    if args.page_id:
        page_id = args.page_id
        page = read_json(paths["interim_dir"] / "pages" / f"{page_id}.json")
        image = Image.open(page["image_path"]).convert("RGB")
        boxes = [
            (box["x1"], box["y1"], box["x2"], box["y2"], box["class_id"])
            for box in page["boxes"]
        ]

    print(f"Página de ejemplo: {page_id}")
    figure_pipeline_general()
    figure_pipeline_imagen()
    figure_letterbox(paths, page_id, image, boxes)
    figure_orientacion()
    figure_iluminacion(paths, page_id)
    figure_arrugas(paths, page_id)
    figure_cajas(paths, page_id, image, boxes)
    figure_folds(paths)
    figure_mapeo_clases()

    condition_grid = FIG_DIR / "condiciones_12.png"
    if condition_grid.exists() and not args.overwrite:
        print(f"  existe, se omite: {condition_grid.name}")
    else:
        print("  condiciones_12.png se genera con scripts/16_make_condition_grid.py")


if __name__ == "__main__":
    main()
