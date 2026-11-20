# Código de análisis — OBR Braille

Pipeline reproducible para el análisis de datos del proyecto de reconocimiento
óptico de Braille Grado 1 con CNN ligera.

## Estado actual

- Corpus derivado **40 páginas × 12 condiciones = 480 imágenes** generado y validado.
- **63/63 clases** cubiertas.
- 5 folds con **24 train / 4 val / 7 test** y **5 páginas externas**.
- `pytest`: 13 pruebas aprobadas.
- Rejilla visual de las 12 condiciones en `reports/figuras/condiciones_12.png`.

## Documentación

- `INFORME_AVANCE_2026-11-13.md`: informe de avance con decisiones, pipeline,
  preprocesamiento, resultados y evidencias.
- `PLAN_ACCION_CORPUS_DERIVADO.md`: plan y estado de ejecución.
- `docs/`: datos, protocolo, metodología, reproducibilidad y App.
- `reports/figuras/`: figuras del pipeline y rejilla de las 12 condiciones.
- `reports/estadistica/REPORTE_DATOS.md`: análisis detallado del corpus.
- `reports/estadistica/REPORTE_DATOS.docx`: versión Word del análisis.

## Requisitos

```bash
python -m pip install -r requirements.txt
```

## Flujo completo

```bash
python scripts/10_audit_sources.py
python scripts/11_build_page_catalog.py
python scripts/12_build_derived_480.py --overwrite
python scripts/13_validate_derived_480.py
python scripts/14_convert_yolo.py
python scripts/15_build_folds.py
python scripts/16_make_condition_grid.py
python scripts/17_make_pipeline_figures.py
python -m pytest -q
```

O con `make`:

```bash
make all
```

## Estructura

```text
configs/                  Rutas, datasets y configuraciones YOLO
data/raw/                 Angelina y DSBI (no se copian; rutas configuradas)
data/interim/pages/       Cajas por página en JSON
data/processed/derived_480/
  images/                 480 imágenes 1024x1024
  labels/                 Etiquetas YOLO normalizadas
  labels_px/              Etiquetas en píxeles
  metadata.csv            Metadatos de las 480 imágenes
data/processed/yolo_derived/
  images/all/             Imágenes para YOLO
  labels/all/             Etiquetas YOLO
  folds/fold_k/data.yaml  Configuración por fold
data/splits/
  page_catalog.csv        Las 40 páginas seleccionadas
  derived_folds.csv       Asignación página/fold/split
  fold_k/                 Listas train/val/test/external
src/data/                 Parsers, catálogo, fotometría, derivación, folds
src/training/             Entrenamiento, exportación ONNX, cuantización INT8
src/evaluation/           Métricas, lectura, robustez, benchmark
src/decoding/             Mapa Braille español Grado 1
src/statistics/           Wilcoxon, McNemar, tamaño del efecto, encuestas
src/deployment/           Inferencia ONNX y contrato Android
scripts/                  Pipeline numerado
tests/                    Pruebas unitarias
docs/                     Datos, protocolo, metodología, reproducibilidad, App
reports/                  Auditoría, validación y figuras
```

## Datos

- **Angelina**: 334 imágenes anotadas, 85,263 cajas, 62/63 clases.
- **DSBI**: 110 páginas `+recto` válidas, 45,627 cajas, 63/63 clases.
- Se excluyen `pics`, `figures`, `+verso`, TXT vacíos y `M+7-??`, `M+9-??`.

Ver `docs/DATOS.md`.

## Corpus derivado

Se seleccionaron 40 páginas:

- 20 Angelina libros.
- 5 Angelina uploaded.
- 10 DSBI `+recto`.
- 5 Angelina manuscritas.

Cada página se transforma en 12 condiciones: iluminación (30°, 45°, difusa) ×
orientación (0°, 15°) × soporte (lisa, arrugas). Ver
`docs/PROTOCOLO_CORPUS.md`.

## Entrenamiento

```bash
python -m src.training.train --config configs/yolov8n_fp32.yaml
```

Las configuraciones `yolov8n_*` y `yolov11_*` apuntan al fold 0. Para los demás
folds, cambia `data` a `data/processed/yolo_derived/folds/fold_k/data.yaml`.

## Evaluación

```bash
python -m src.evaluation.evaluate --weights outputs/runs/yolov8n_fp32/weights/best.pt --data data/processed/yolo_derived/folds/fold_0/data.yaml
```

## Exportación y App

```bash
python -m src.training.export_onnx --weights best.pt --output outputs/models/model.onnx
python -m src.training.quantize_int8 --input outputs/models/model.onnx --output outputs/models/model_int8.onnx
python -m src.deployment.infer --model outputs/models/model_int8.onnx --image ruta.jpg
```

Ver `docs/APP.md` y `src/deployment/android_contract.md`.

## Limitaciones

- El corpus es **derivado**, no de campo.
- Las fuentes son multilingües; el detector es agnóstico al idioma a nivel de
  celda, pero la evaluación no es “español”.
- Las 5 manuscritas no garantizan errores ortográficos reales.
- La cuantización INT8 está implementada en modo dinámico; la estática con
  calibración queda como `TODO`.
- Requiere aprobación del asesor antes del experimento final.
