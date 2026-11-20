# Plan de acción: corpus derivado 40 × 12

**Proyecto:** Diseño y evaluación de una red neuronal convolucional ligera para el
reconocimiento óptico de Braille Grado 1 en dispositivos móviles.

**Autores:** Rony Frank Churata Huania; Erick Jean Ramos Vera.

**Fecha:** 13 de noviembre de 2026.

**Estado:** plan aprobado para ejecución; pendiente de aprobación del asesor
sobre el uso del corpus derivado.

---

## 1. Decisión

Se construirá un **corpus derivado** de 40 páginas × 12 condiciones
fotométricas = **480 imágenes**, usando únicamente los datasets ya descargados:

- **Angelina Braille Dataset** (`data 1/AngelinaDataset`).
- **DSBI** (`data 2/DSBI`), solo imágenes `+recto`.

No se usarán por ahora Kaggle, Roboflow ni ScienceDB.

El corpus se declarará como **derivado**, no como corpus de campo. La aprobación
del asesor es requisito antes de ejecutar el experimento final.

---

## 2. Auditoría de las fuentes

### Angelina

| Métrica | Valor |
|---|---|
| Imágenes anotadas | 334 |
| Libros | 212 |
| Manuscritas | 28 |
| No-Braille | 44 |
| Uploaded | 50 |
| Cajas | 85,263 |
| Clases | 62/63; falta la clase 41 |
| Desbalance | mínimo 2, máximo 7,472 |
| Duplicados | 0 |
| Tamaños | 1024×1376, 1024×768, 813×600 |
| Commit | `e13038d` (2023-06-05) |

### DSBI

| Métrica | Valor |
|---|---|
| Imágenes | 114 originales + 114 `+recto` + 114 `+verso` |
| Anotaciones | 228 TXT; 91,443 celdas |
| Clases | 63/63 |
| Desbalance | mínimo 168, máximo 4,287 |
| TXT vacíos | 8 (4 recto y 4 verso) |
| TXT no estándar | `M+7-??.txt`, `M+9-??.txt` |
| Duplicados | 90 pares `+recto`/`+verso` idénticos |
| Tamaños | originales 1700×2338; recto/verso 1732×2361 |
| Commit | `6937eb8` (2018-12-19) |

---

## 3. Selección de las 40 páginas

| Fuente | Páginas |
|---|---:|
| Angelina `books` | 20 |
| Angelina `uploaded` | 5 |
| DSBI `+recto` | 10 |
| Angelina `handwritten` | 5 |
| **Total** | **40** |

Criterios:

- Cubrir las **63 clases**, incluida la clase 41 ausente en Angelina.
- Priorizar páginas DSBI con clases raras.
- Las 5 manuscritas se usarán como aproximación a “producciones espontáneas”.
  Si no contienen errores reales, se documentará esa limitación.
- Cada página recibe un `page_id` único y permanece íntegra en todos sus folds.

### Exclusiones

- `pics/` de Angelina.
- `not_braille` para las 40 páginas (puede usarse luego como negativos).
- `figures/` de DSBI.
- `+verso` de DSBI.
- TXT `+recto` vacíos: `FM+14`, `M+2`, `SVNGCB1+2`, `SVNGCB2+2`.
- `M+7-??.txt` y `M+9-??.txt`.

---

## 4. Las 12 condiciones

| Factor | Niveles |
|---|---|
| Iluminación | rasante 30°, rasante 45°, difusa |
| Orientación | 0° ortogonal, 15° inclinada |
| Soporte | hoja lisa, hoja con arrugas/pliegues |

Implementación:

- **Iluminación:** gradiente direccional + sombra gaussiana; no mueve cajas.
- **Orientación:** homografía de 15°; se transforman las esquinas de cada caja.
- **Arrugas:** deformación elástica suave + sombras de pliegue; se aplica la misma
  deformación a las cajas y se valida que sigan dentro de la imagen.
- Resolución canónica: 1024×1024 con letterbox; entrenamiento con `imgsz=640`.
- Cada condición guarda semilla y parámetros en `metadata.csv`.

---

## 5. Folds y conteos

| Partición | Páginas | Condiciones | Imágenes |
|---|---:|---:|---:|
| Entrenamiento | 24 | 12 | 288 |
| Validación | 4 | 12 | 48 |
| Prueba (pliegue) | 7 | 12 | 84 |
| Prueba externa | 5 | 12 | 60 |
| **Total** | **40** | **12** | **480** |

- 35 páginas controladas → 5 folds de 7.
- En cada iteración: 24 train, 4 val, 7 test.
- Las 5 manuscritas quedan como prueba externa.
- Las 12 condiciones de una página siempre caen en la misma partición.

---

## 6. Estructura del proyecto de código

```text
06_Codigo_Analisis/
├── README.md
├── requirements.txt
├── environment.yml
├── Makefile
├── .gitignore
├── configs/
│   ├── paths.example.yaml
│   ├── datasets/
│   │   ├── angelina.yaml
│   │   ├── dsbi.yaml
│   │   └── derived_480.yaml
│   ├── yolov8n_fp32.yaml
│   ├── yolov8n_int8.yaml
│   ├── yolov11_fp32.yaml
│   └── yolov11_int8.yaml
├── data/
│   ├── raw/
│   │   ├── angelina/
│   │   └── dsbi/
│   ├── processed/
│   │   ├── derived_480/
│   │   │   ├── images/
│   │   │   ├── labels/
│   │   │   └── metadata.csv
│   │   └── yolo_derived/
│   └── splits/
│       └── derived_folds.csv
├── src/
│   ├── data/
│   │   ├── sources/
│   │   │   ├── angelina.py
│   │   │   ├── dsbi.py
│   │   │   └── registry.py
│   │   ├── class_mapping.py
│   │   ├── page_catalog.py
│   │   ├── photometric.py
│   │   ├── derive_corpus.py
│   │   ├── convert_yolo.py
│   │   ├── build_folds.py
│   │   ├── dedupe.py
│   │   └── validate.py
│   ├── training/
│   │   ├── train.py
│   │   ├── export_onnx.py
│   │   └── quantize_int8.py
│   ├── evaluation/
│   │   ├── evaluate.py
│   │   ├── metrics.py
│   │   ├── robustness.py
│   │   ├── benchmark.py
│   │   └── reading_order.py
│   ├── decoding/
│   │   ├── braille_map.py
│   │   └── decode.py
│   ├── statistics/
│   │   ├── tests.py
│   │   ├── effect_size.py
│   │   └── surveys.py
│   ├── deployment/
│   │   ├── infer.py
│   │   └── android_contract.md
│   └── utils/
│       ├── seed.py
│       ├── logging.py
│       ├── paths.py
│       └── io.py
├── scripts/
│   ├── 10_audit_sources.py
│   ├── 11_build_page_catalog.py
│   ├── 12_build_derived_480.py
│   ├── 13_validate_derived_480.py
│   ├── 14_convert_yolo.py
│   └── 15_build_folds.py
├── tests/
│   ├── test_class_mapping.py
│   ├── test_photometric.py
│   ├── test_derive.py
│   └── test_folds.py
├── outputs/
│   ├── runs/
│   ├── models/
│   ├── metrics/
│   └── figures/
├── docs/
│   ├── DATOS.md
│   ├── PROTOCOLO_CORPUS.md
│   ├── METODOLOGIA.md
│   ├── REPRODUCIBILIDAD.md
│   └── APP.md
└── reports/
    ├── tablas/
    └── figuras/
```

---

## 7. Flujo de ejecución

1. `10_audit_sources.py`: auditar Angelina y DSBI.
2. `11_build_page_catalog.py`: seleccionar 40 páginas y verificar 63/63 clases.
3. `12_build_derived_480.py`: generar 480 imágenes, etiquetas y metadata.
4. `13_validate_derived_480.py`: validar 480 imágenes, 40 páginas, 12 condiciones,
   5 folds y cajas.
5. `14_convert_yolo.py`: generar `images/`, `labels/` y `data.yaml`.
6. `15_build_folds.py`: generar splits 24/4/7 + 5 externas.
7. Entrenamiento, evaluación y estadística: wrappers con `TODO`.

---

## 8. Validación

- 480 imágenes, 40 `page_id`, 12 condiciones por página.
- 63/63 clases cubiertas; reporte de distribución.
- Cajas válidas después de iluminación, orientación y arrugas.
- Cero páginas compartidas entre train/val/test.
- Rejilla visual con las 12 condiciones de una página.
- `pytest` para mapeo de clases, transformaciones y folds.

---

## 9. Limitaciones

- El corpus es **derivado**, no de campo.
- Las fuentes son multilingües (ruso/inglés/chino). El detector es agnóstico al
  idioma a nivel de celda, pero la evaluación no será “español”.
- Las 5 manuscritas no garantizan errores ortográficos reales.
- Requiere aprobación del asesor antes del experimento final.
- Si no se aprueba, el fallback es recolectar las 40 páginas o cambiar a un
  corpus multi-fuente.

---

## 10. Preparado para la App

- `export_onnx.py` y `quantize_int8.py` con `TODO` y CLI.
- `deployment/infer.py` con contrato de entrada/salida.
- `decoding/braille_map.py` con mapa español Grado 1 incompleto.
- `android_contract.md` con forma del tensor, NMS, umbral de confianza y JSON
  de salida.

---

## 11. Pendientes

- Aprobación del asesor sobre el corpus derivado.
- Confirmar la composición de las 40 páginas.
- Confirmar que la clase 41 queda cubierta por las páginas DSBI seleccionadas.
- Definir si las 5 manuscritas se aceptan como “espontáneas” o se renombran.

---

## 12. Estado de ejecución (13 de noviembre de 2026)

- [x] Estructura `06_Codigo_Analisis/` creada.
- [x] Auditoría: Angelina 334 imágenes, 85,263 cajas, 62 clases; DSBI 110 páginas
  `+recto` válidas, 45,627 cajas, 63 clases.
- [x] Catálogo: 40 páginas, 63/63 clases, folds 7/7/7/7/7.
- [x] Corpus derivado: 480 imágenes, 141,444 cajas, 81.9 MB.
- [x] Validación: 480 imágenes, 40 páginas, 12 condiciones, 63 clases,
  folds 24/4/7 + 5 externas.
- [x] YOLO: 480 imágenes + etiquetas + `data.yaml`.
- [x] Folds: 5 folds + prueba externa.
- [x] Rejilla visual: `reports/figuras/condiciones_12.png`.
- [x] `pytest`: 13 pruebas aprobadas.
- [ ] Aprobación del asesor.
- [ ] Entrenamiento y evaluación final de las 4 configuraciones × 5 folds.

