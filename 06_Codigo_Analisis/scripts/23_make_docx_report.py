import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.io import ensure_dir

STATS_DIR = ROOT / "reports" / "estadistica"
FIGURES_DIR = ROOT / "reports" / "figuras"
OUTPUT = STATS_DIR / "REPORTE_DATOS.docx"

TABLE_COUNTER = 0
FIGURE_COUNTER = 0


def _set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def _repeat_header(table):
    tr = table.rows[0]._tr
    tr_pr = tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def _format_value(value, column):
    if pd.isna(value):
        return ""
    if "p_valor" in column or "p_value" in column:
        return f"{float(value):.3e}"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def add_caption(doc, text, bold=False, italic=False, size=9):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    return paragraph


def add_table(doc, frame, caption, font_size=9, landscape=False):
    global TABLE_COUNTER
    TABLE_COUNTER += 1
    add_caption(doc, f"Tabla {TABLE_COUNTER}. {caption}", bold=True, size=9)
    table = doc.add_table(rows=1, cols=len(frame.columns))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    header = table.rows[0].cells
    for index, column in enumerate(frame.columns):
        header[index].text = str(column)
        _set_cell_shading(header[index], "D9E2F3")
    for _, row in frame.iterrows():
        cells = table.add_row().cells
        for index, column in enumerate(frame.columns):
            cells[index].text = _format_value(row[column], column)
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(font_size)
    _repeat_header(table)
    doc.add_paragraph()
    return table


def add_figure(doc, filename, caption, width_cm=16):
    global FIGURE_COUNTER
    path = FIGURES_DIR / filename
    if not path.exists():
        add_caption(doc, f"[Falta la figura: {filename}]", italic=True)
        return
    FIGURE_COUNTER += 1
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    caption_paragraph = doc.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption_paragraph.add_run(f"Figura {FIGURE_COUNTER}. {caption}")
    run.italic = True
    run.font.size = Pt(9)
    run.font.name = "Times New Roman"
    doc.add_paragraph()


def add_field(paragraph, field):
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = field
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_toc(doc):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = 'TOC \\o "1-2" \\h \\z \\u'
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Actualiza el índice en Word: clic derecho > Actualizar campo."
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr_text)
    run._r.append(fld_char2)
    run._r.append(text)
    run._r.append(fld_char3)


def add_header_footer(section):
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    header = section.header.paragraphs[0]
    header.text = "Análisis de datos — Proyecto Braille OBR"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Página ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)
    add_field(footer, "PAGE")
    run = footer.add_run(" de ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)
    add_field(footer, "NUMPAGES")


def new_section(doc, landscape):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    section.different_first_page_header_footer = False
    section.header.is_linked_to_previous = True
    section.footer.is_linked_to_previous = True
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Cm(29.7)
        section.page_height = Cm(21.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
    return section


def add_heading(doc, text, level=1, page_break=False):
    if page_break:
        doc.add_page_break()
    doc.add_heading(text, level=level)


def main():
    parser = argparse.ArgumentParser(description="Genera el DOCX del análisis de datos")
    parser.add_argument("--output", default=str(OUTPUT))
    args = parser.parse_args()

    resumen = pd.read_csv(STATS_DIR / "datos_resumen.csv")
    clases = pd.read_csv(STATS_DIR / "datos_clases.csv")
    fuentes = pd.read_csv(STATS_DIR / "datos_fuentes.csv")
    subconjuntos = pd.read_csv(STATS_DIR / "datos_subconjuntos.csv")
    condiciones = pd.read_csv(STATS_DIR / "datos_condiciones.csv")
    folds = pd.read_csv(STATS_DIR / "datos_folds.csv")
    with open(STATS_DIR / "datos_pruebas.json", "r", encoding="utf-8") as handle:
        pruebas = json.load(handle)
    with open(STATS_DIR / "datos_duplicados.json", "r", encoding="utf-8") as handle:
        duplicados = json.load(handle)

    resumen_dict = dict(zip(resumen["metrica"], resumen["valor"]))
    n_imagenes = int(resumen_dict["imagenes"])
    n_paginas = int(resumen_dict["paginas"])
    n_condiciones = int(resumen_dict["condiciones"])
    n_cajas = int(resumen_dict["cajas"])
    n_clases = int(resumen_dict["clases"])
    desbalance = pruebas["desbalance"]
    top15 = clases.sort_values("count", ascending=False).head(15)
    fold_table = folds.copy()
    fold_table["split"] = pd.Categorical(
        fold_table["split"], categories=["train", "val", "test", "external"], ordered=True
    )
    fold_table = fold_table.sort_values(["experiment_fold", "split"])

    test_rows = []
    for name, result in pruebas.items():
        if isinstance(result, dict) and "p_value" in result and "statistic" in result:
            test_rows.append(
                {
                    "prueba": name,
                    "n": result.get("n"),
                    "estadistico": result.get("statistic"),
                    "p_valor": result.get("p_value"),
                }
            )
    tests = pd.DataFrame(test_rows)
    other_rows = [
        {"metrica": "jensen_shannon_angelina_dsbi", "valor": pruebas["jensen_shannon_angelina_dsbi"]},
        {"metrica": "cajas_por_pagina_bootstrap_ci95", "valor": str(pruebas["cajas_por_pagina_bootstrap_ci95"])},
    ] + [{"metrica": key, "valor": value} for key, value in desbalance.items()]
    other = pd.DataFrame(other_rows)

    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.different_first_page_header_footer = True
    add_header_footer(section)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)
    for style_name, size, color in [
        ("Heading 1", 16, RGBColor(0x1F, 0x3A, 0x5F)),
        ("Heading 2", 13, RGBColor(0x1F, 0x3A, 0x5F)),
        ("Heading 3", 11, RGBColor(0x1F, 0x3A, 0x5F)),
    ]:
        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color

    settings = doc.settings.element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)

    # Portada
    for _ in range(5):
        doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Análisis detallado del corpus derivado")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(24)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(
        "Diseño y evaluación de una red neuronal convolucional ligera para el "
        "reconocimiento óptico de Braille Grado 1 en dispositivos móviles"
    )
    run.italic = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    doc.add_paragraph()
    for text in [
        "Rony Frank Churata Huania",
        "Erick Jean Ramos Vera",
        "Escuela Profesional de Ingeniería de Sistemas e Informática",
        "Universidad Nacional de Moquegua",
        "Trabajo de Investigación",
        "Noviembre de 2026",
        "https://github.com/ronyC25/Proyecto-Braille-",
    ]:
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)

    # Índice
    doc.add_page_break()
    content = doc.add_paragraph()
    run = content.add_run("Contenido")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    add_toc(doc)

    # Resumen ejecutivo
    add_heading(doc, "Resumen ejecutivo", level=1, page_break=True)
    doc.add_paragraph(
        f"El corpus derivado contiene {n_imagenes} imágenes ({n_paginas} páginas × "
        f"{n_condiciones} condiciones), {n_cajas:,} cajas anotadas y {n_clases}/63 "
        "clases Braille cubiertas. Se construyó a partir de Angelina y DSBI +recto. "
        "El análisis se centra en composición, balance, calidad de imagen, área de "
        "caja y cobertura por fold; no incluye entrenamiento de modelos."
    )
    key = pd.DataFrame(
        [
            ("Imágenes", f"{n_imagenes}"),
            ("Páginas", f"{n_paginas}"),
            ("Condiciones", f"{n_condiciones}"),
            ("Cajas", f"{n_cajas:,}"),
            ("Clases cubiertas", f"{n_clases}/63"),
            ("Cajas por página (media)", f"{resumen_dict['cajas_por_pagina_media']:.1f}"),
            ("Cajas por página (mediana)", f"{resumen_dict['cajas_por_pagina_mediana']:.0f}"),
            ("Área media de caja (px²)", f"{resumen_dict['area_caja_media_px2']:.1f}"),
            ("Brillo medio", f"{resumen_dict['brillo_medio']:.1f}"),
            ("Contraste medio", f"{resumen_dict['contraste_medio']:.1f}"),
            ("Nitidez media", f"{resumen_dict['nitidez_media']:.1f}"),
        ],
        columns=["Indicador", "Valor"],
    )
    add_table(doc, key, "Indicadores principales del corpus", font_size=9)

    # 1. Resumen del corpus
    add_heading(doc, "1. Resumen del corpus", level=1, page_break=True)
    doc.add_paragraph(
        "La Tabla 2 presenta las métricas generales del corpus. Todas las imágenes "
        "tienen resolución 1024×1024 y las anotaciones están en formato YOLO."
    )
    add_table(doc, resumen.rename(columns={"metrica": "Métrica", "valor": "Valor"}),
              "Resumen general del corpus", font_size=9)

    # 2. Composición
    add_heading(doc, "2. Composición por fuente y subconjunto", level=1, page_break=True)
    doc.add_paragraph(
        "Angelina aporta 30 páginas y 58 clases; DSBI +recto aporta 10 páginas y "
        "las 63 clases. La combinación de ambas fuentes cubre todo el espacio de "
        "clases Braille."
    )
    add_table(doc, fuentes, "Composición por fuente", font_size=9)
    add_table(doc, subconjuntos, "Composición por subconjunto", font_size=9)
    add_figure(doc, "datos_distribucion_fuente.png",
               "Distribución de clases por fuente (Angelina vs. DSBI)", width_cm=16)

    # 3. Distribución de clases
    add_heading(doc, "3. Distribución de clases", level=1, page_break=True)
    doc.add_paragraph(
        f"Las 63 clases están presentes, pero su frecuencia es desigual. La clase "
        f"más frecuente concentra {int(clases['count'].max()):,} cajas y la menos "
        f"frecuente {int(clases[clases['count'] > 0]['count'].min()):,}. La Tabla 5 "
        "muestra las 15 clases más frecuentes; el anexo contiene la tabla completa."
    )
    add_table(doc, top15[["int_label", "dots", "count", "pct", "count_angelina", "count_dsbi"]],
              "Top 15 clases por cantidad de cajas", font_size=9)
    add_figure(doc, "datos_distribucion.png",
               "Distribución de las 63 clases y porcentaje acumulado", width_cm=16)

    # 4. Desbalance
    add_heading(doc, "4. Desbalance de clases", level=1, page_break=True)
    doc.add_paragraph(
        "El desbalance es alto: la razón entre la clase más y menos frecuente es "
        f"{desbalance['ratio_max_min']:.1f}. Se recomienda augmentation selectiva y "
        "class weights durante el entrenamiento."
    )
    add_table(doc, pd.DataFrame(list(desbalance.items()), columns=["Métrica", "Valor"]),
              "Métricas de desbalance de clases", font_size=9)

    # 5. Cajas por página y condición
    add_heading(doc, "5. Cajas por página y por condición", level=1, page_break=True)
    doc.add_paragraph(
        f"Cada página contiene entre {int(resumen_dict['cajas_por_pagina_min'])} y "
        f"{int(resumen_dict['cajas_por_pagina_max'])} cajas; la mediana es "
        f"{resumen_dict['cajas_por_pagina_mediana']:.0f}."
    )
    add_figure(doc, "datos_cajas_pagina.png",
               "Distribución de cajas por página", width_cm=16)
    doc.add_paragraph(
        "La Tabla 7 resume las 12 condiciones. La iluminación no altera el área de "
        "caja; la orientación y el soporte sí lo hacen."
    )
    new_section(doc, landscape=True)
    add_table(doc, condiciones, "Resumen de las 12 condiciones", font_size=8)
    add_figure(doc, "datos_area_caja.png",
               "Área media de caja por condición", width_cm=24)
    new_section(doc, landscape=False)

    # 6. Calidad de imagen
    add_heading(doc, "6. Calidad de imagen", level=1)
    doc.add_paragraph(
        "Las condiciones modifican significativamente el brillo, el contraste y la "
        "nitidez (p < 0.001). La Figura 5 muestra la distribución por iluminación, "
        "orientación y soporte."
    )
    add_figure(doc, "datos_calidad.png",
               "Calidad de imagen por condición", width_cm=16)

    # 7. Pruebas estadísticas
    add_heading(doc, "7. Pruebas estadísticas", level=1, page_break=True)
    doc.add_paragraph(
        "Se aplicaron pruebas de Friedman para la iluminación y Wilcoxon pareado "
        "para orientación y soporte. Los valores p se reportan en notación científica."
    )
    add_table(doc, tests, "Pruebas de Friedman y Wilcoxon", font_size=9)
    add_table(doc, other, "Otras métricas: JSD, bootstrap y desbalance", font_size=9)

    # 8. Cobertura por fold
    add_heading(doc, "8. Cobertura por fold", level=1, page_break=True)
    doc.add_paragraph(
        "Los cinco conjuntos de entrenamiento cubren 63/63 clases. Validación, prueba "
        "y externo no cubren todas las clases, lo cual es esperado por su tamaño."
    )
    add_figure(doc, "datos_cobertura_folds.png",
               "Cobertura de clases por fold y split", width_cm=16)
    new_section(doc, landscape=True)
    add_table(doc, fold_table, "Cobertura y conteos por fold y split", font_size=8)
    new_section(doc, landscape=False)

    # 9. Integridad
    add_heading(doc, "9. Integridad y duplicados", level=1)
    doc.add_paragraph(f"Grupos de imágenes duplicadas: {duplicados['n_duplicados']}.")
    doc.add_paragraph("Todas las imágenes tienen tamaño 1024×1024.")
    doc.add_paragraph(f"Clases cubiertas: {n_clases}/63.")

    # 10. Conclusiones
    add_heading(doc, "10. Conclusiones del análisis de datos", level=1, page_break=True)
    conclusions = [
        "El corpus está balanceado por página y condición: 40 imágenes por condición y 12 imágenes por página.",
        f"La distribución de clases es desigual: la clase más frecuente tiene {int(clases['count'].max()):,} cajas y la menos frecuente {int(clases[clases['count'] > 0]['count'].min()):,}.",
        "DSBI aporta 63/63 clases y Angelina 58/63; la combinación cubre el espacio completo.",
        "La orientación y el soporte modifican el área de caja; la iluminación no (p≈0.542).",
        "La cobertura de entrenamiento es 63/63 en todos los folds; val/test/external no cubren todas las clases, algo esperado por su tamaño.",
        "El desbalance es alto (ratio máximo/mínimo ≈ 90.9), por lo que se recomienda augmentation y class weights.",
    ]
    for text in conclusions:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.add_run(text)

    # 11. Anexo
    new_section(doc, landscape=True)
    add_heading(doc, "11. Anexo: tabla completa de clases", level=1)
    doc.add_paragraph(
        "La Tabla 11 contiene las 63 clases con su frecuencia total, por fuente y por subconjunto."
    )
    add_table(
        doc,
        clases[
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
        ],
        "Tabla completa de clases",
        font_size=7.5,
    )

    output = Path(args.output)
    ensure_dir(output.parent)
    doc.save(output)
    print(f"DOCX generado: {output}")
    print(f"Tablas: {TABLE_COUNTER} | Figuras: {FIGURE_COUNTER}")


if __name__ == "__main__":
    main()
