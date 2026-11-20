# Reproducibilidad

## Entorno verificado

| Componente | Versión |
|---|---|
| Python | 3.11.9 |
| numpy | 2.4.4 |
| opencv-python | 4.11.0 |
| Pillow | 12.2.0 |
| PyYAML | 6.0.3 |
| pandas | 2.3.3 |
| scipy | 1.17.1 |
| scikit-learn | 1.9.0 |
| ultralytics | 8.4.82 |
| onnxruntime | 1.31.1 |

## Instalación

```bash
python -m pip install -r requirements.txt
```

## Ejecución completa

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

## Semillas

- Catálogo: `seed=42`.
- Corpus: `seed = 42 + page_index * 100 + condition_index`.
- Folds: derivados del catálogo, sin aleatoriedad adicional.

## Salidas esperadas

| Archivo | Contenido |
|---|---|
| `data/splits/page_catalog.csv` | 40 páginas seleccionadas |
| `data/processed/derived_480/metadata.csv` | 480 filas |
| `data/splits/derived_folds.csv` | Asignación página/fold/split |
| `reports/auditoria_fuentes.json` | Auditoría de Angelina y DSBI |
| `reports/validacion_derived_480.json` | Validación del corpus |
| `reports/figuras/condiciones_12.png` | Rejilla visual |

## Figuras del pipeline

`python scripts/17_make_pipeline_figures.py` genera:

- `pipeline_general.png`
- `pipeline_imagen.png`
- `letterbox.png`
- `orientacion.png`
- `iluminacion.png`
- `arrugas.png`
- `cajas_transformadas.png`
- `folds.png`
- `mapeo_clases.png`

La rejilla de 12 condiciones se genera con
`python scripts/16_make_condition_grid.py`.

## Comprobaciones

- 480 imágenes, 40 páginas, 12 condiciones.
- 63/63 clases.
- Folds 24/4/7 + 5 externas.
- `pytest`: 13 pruebas.

## Nota

No se versionan las imágenes crudas ni las salidas. Las rutas se configuran en
`configs/paths.yaml`.
