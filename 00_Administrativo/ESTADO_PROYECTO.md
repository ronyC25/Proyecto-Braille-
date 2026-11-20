# Estado y continuidad del proyecto

> **Archivo de seguimiento.** Fuente única de verdad sobre el estado, decisiones, pendientes y riesgos del proyecto. Actualizar al final de cada sesión de trabajo.

---

## 1. Ficha del proyecto

| Campo | Valor |
|---|---|
| **Título vigente** | Diseño y evaluación de una red neuronal convolucional ligera para el reconocimiento óptico de Braille Grado 1 en dispositivos móviles: efecto en la retroalimentación docente en aulas inclusivas de Moquegua e Ilo |
| **Autores** | Rony Frank Churata Huania; Erick Jean Ramos Vera |
| **Institución** | Escuela Profesional de Ingeniería de Sistemas e Informática, Universidad Nacional de Moquegua |
| **Curso** | Trabajo de Investigación |
| **Docente / asesor** | *[Nombre del docente o asesor]* — **pendiente de completar en portada** |
| **Fecha en portada** | 8 de octubre de 2026 *(verificar/actualizar)* |
| **Última actualización de este registro** | 13 de noviembre de 2026 |
| **Archivo canónico** | `Unidad 1/Trabajo Investigacion/01_Proyecto_Tesis/Proyecto_OBR_Braille_APA7.docx` |
| **Estado general** | Corpus derivado 480 listo y validado; pendiente aprobación del asesor, umbrales `[VERIFICAR]` y entrenamiento final |
| **Formato** | APA 7.ª edición (Times New Roman 12, interlineado doble, márgenes 2.54 cm, numeración de página) |

---

## 2. Encuadre y alcance

**Encuadre B — Ingeniería / CNN.** El objeto de estudio es la **red neuronal convolucional ligera** y su desempeño en dispositivos móviles. La evaluación del efecto en la retroalimentación docente es el **tercer objetivo**, no el eje principal.

| Elemento | Definición |
|---|---|
| **Núcleo** | Diseño y evaluación comparativa de configuraciones CNN para OBR en móvil |
| **Objeto** | Arquitectura de detección (YOLOv8n vs. YOLOv11) y cuantización (FP32 vs. INT8) |
| **Resultado principal** | Desempeño del detector: precisión (incl. robustez) y eficiencia |
| **Componente pedagógico** | Tercer objetivo: efecto en la oportunidad de la retroalimentación |
| **Línea de investigación UNAM** | **«Desarrollo y aplicaciones de la inteligencia artificial»** |

---

## 3. Bitácora de decisiones

| Fecha | Decisión | Justificación |
|---|---|---|
| — | Corrección de aritmética del dataset: 12 combinaciones (no 10), 480 fotos, aumento solo en train | Coherencia interna y prevención de fuga de datos |
| — | Corrección de citas: BraUNet (Li et al., 2020) y YOLOv11 (Sun et al., 2025) | Autor/año/título/páginas verificados |
| — | Título con «CNN» y sin «Grado 1» → se restituyó «Grado 1» | Coherencia con el alcance real (Grado 1) |
| — | Formato APA 7 (fuente, márgenes, interlineado, títulos, referencias, tablas) | Presentación formal |
| — | Portada APA con autores reales | Identificación del trabajo |
| — | **Cambio a Encuadre B (ingeniería/CNN)** | El núcleo es construir/evaluar la CNN para móvil |
| — | **Reducción a 3 objetivos/hipótesis** | Enfoque y correspondencia uno a uno |
| — | **Inclusión de Kappa, AUC-ROC y F1** | Evaluación completa: concordancia, discriminabilidad y balance |
| — | Robustez como faceta de la precisión | Evita un objetivo extra; se mide como ΔmAP/CER en condiciones adversas |
| — | Autor metodológico: **Hernández-Sampieri y Mendoza (2018)** | Tipo, nivel, enfoque y diseño generales |
| — | DSR (Hevner et al., 2004; Peffers et al., 2007) solo para la Fase A | Marco de desarrollo del artefacto |
| — | Se añadieron referencias Brooke (1996), Hart y Staveland (1988), Hattie y Timperley (2007) | Sustento de SUS, NASA-TLX y feedback |
| 12 nov 2026 | Reorganización de `Trabajo Investigacion` por tipo de entregable (00–04) | Evitar la mezcla de documento, artículo, evidencias y respaldos |
| 12 nov 2026 | Corrección de compilación Overleaf: `latexmkrc` fuerza XeLaTeX | `fontspec` no compila con pdfLaTeX |
| 13 nov 2026 | Creación de plantillas APA 7 para proyecto y artículo en `05_Plantillas/` | Reutilización del formato y bibliografía automática |
| 13 nov 2026 | Creación de `06_Codigo_Analisis/` y corpus derivado 480 (40 × 12) | Pipeline reproducible; 63/63 clases; folds 24/4/7 + 5 externas |
| 13 nov 2026 | Informe de avance del análisis de datos | Documenta decisiones, pipeline, preprocesamiento y evidencias |

---

## 4. Definiciones canónicas

### 4.1 Problema general (PG)
> ¿Qué configuración de una red neuronal convolucional ligera —combinación de arquitectura (YOLOv8n o YOLOv11) y esquema de cuantización (FP32 o INT8)— ofrece el mejor compromiso entre precisión (incluida la robustez), eficiencia computacional y oportunidad de la retroalimentación docente en dispositivos móviles?

### 4.2 Problemas específicos (PE)
1. **PE1.** ¿Qué configuración (arquitectura × cuantización) ofrece mayor precisión y robustez, medida con mAP@0.5, F1 macro, Kappa de Cohen y AUC-ROC macro, en condiciones normales y adversas?
2. **PE2.** ¿En qué medida la cuantización INT8 reduce la latencia y el consumo de memoria del modelo sin degradar su precisión más allá de un umbral aceptable?
3. **PE3.** ¿Qué efecto tiene el uso del sistema en la oportunidad de la retroalimentación docente (tiempo de revisión por página) en aulas inclusivas de Moquegua e Ilo?

### 4.3 Objetivo general (OG)
> Evaluar el desempeño de configuraciones de una red neuronal convolucional ligera para el reconocimiento óptico de Braille Grado 1 en dispositivos móviles, con el fin de identificar la que ofrece el mejor compromiso entre precisión (incluida la robustez), eficiencia y oportunidad de la retroalimentación docente.

### 4.4 Objetivos específicos (OE)
1. **OE1.** Comparar la precisión y la robustez de las configuraciones evaluadas mediante mAP@0.5, F1 macro, Kappa de Cohen y AUC-ROC macro.
2. **OE2.** Determinar el efecto de la cuantización INT8 sobre la latencia, la memoria y la precisión del modelo.
3. **OE3.** Evaluar el efecto del sistema en el tiempo de revisión por página de los docentes.

### 4.5 Hipótesis
- **HG.** La configuración YOLOv11 cuantizada a INT8 ofrece el mejor compromiso entre precisión (incluida la robustez) y eficiencia, y reduce el tiempo de revisión docente frente a las demás configuraciones evaluadas.
- **H0.** No existen diferencias estadísticamente significativas entre configuraciones en precisión, robustez o eficiencia, ni efecto del sistema sobre el tiempo de revisión.
- **H1.** YOLOv11 supera a YOLOv8n en mAP@0.5 y F1 macro (Wilcoxon; p < .05) y mantiene la ventaja en condiciones adversas (robustez).
- **H2.** La cuantización INT8 reduce la latencia y el consumo de memoria con una degradación de mAP@0.5 no superior a `[VERIFICAR]` puntos porcentuales (criterio de no inferioridad; IC bootstrap al 95 %).
- **H3.** El uso del sistema reduce el tiempo de revisión por página respecto del procedimiento habitual (Wilcoxon; p < .05).

---

## 5. Variables y operacionalización

| Variable | Rol | Dimensión | Indicadores |
|---|---|---|---|
| Arquitectura de detección CNN | Independiente | Arquitectura / Cuantización | YOLOv8n, YOLOv11; FP32, INT8 |
| Desempeño del detector | Dependiente | Precisión (incl. robustez) | mAP@0.5, mAP@0.5:0.95, F1 macro, Kappa, AUC-ROC macro OVR, CER, WER, Δ en condiciones adversas |
| Desempeño del detector | Dependiente | Eficiencia | Latencia (ms), RAM (MB), tamaño (MB), ΔmAP |
| Retroalimentación evaluativa docente | Secundaria | Oportunidad | Tiempo de revisión por página (min) |
| Carga cognitiva docente | Secundaria | Carga global | NASA-TLX (0–100) |
| Usabilidad del sistema | Secundaria | Usabilidad global | SUS (0–100) |

> **Regla:** la VI es un concepto con **niveles**; las métricas técnicas son indicadores de la VD, no de la VI. Los hiperparámetros y el protocolo van en la metodología.

---

## 6. Metodología

| Subsección | Definición |
|---|---|
| **Línea** | «Desarrollo y aplicaciones de la inteligencia artificial» (UNAM) |
| **Enfoque** | Cuantitativo |
| **Tipo** | Aplicada / desarrollo tecnológico |
| **Nivel** | Explicativo / comparativo |
| **Diseño** | Experimental comparativo (manipulación sobre el sistema, baseline YOLOv8n FP32, aleatorización de particiones/semillas) + evaluación pedagógica cuasiexperimental |
| **Autor metodológico** | Hernández-Sampieri y Mendoza (2018); DSR para la Fase A |

**Criterios del diseño:** (a) aleatorización de datos, no de sujetos; (b) manipulación sobre el sistema; (c) control = baseline YOLOv8n FP32.

**Protocolo:** documentar versiones de Python, PyTorch, Ultralytics YOLO, ONNX Runtime y Android; características del dispositivo; semillas fijas; conservar código, pesos y particiones.

---

## 7. Datos y muestra

| Elemento | Valor |
|---|---|
| Corpus | 40 páginas (35 controladas + 5 de producciones espontáneas) |
| Fotografías originales | 480 (40 × 12 combinaciones) |
| Aumento de datos | Solo entrenamiento: 288 × 6 = 1728 |
| Total de imágenes | 2208 |
| Partición | Validación cruzada de 5 pliegues agrupada por página |
| Prueba externa | 5 páginas espontáneas |
| Muestra docente | Hasta 30 docentes (UGEL Ilo y Mariscal Nieto) |
| Potencia | t pareada, α = .05, 1−β = .80, d = 0.55 → 27–28 pares; 30 con 10 % de atrición |
| Fuga de datos | Evitada: partición por página antes del aumento |

---

## 8. Métricas y pruebas

| Métrica | Qué mide | Uso |
|---|---|---|
| mAP@0.5 / mAP@0.5:0.95 | Precisión de detección | Comparación principal (H1) |
| **F1 macro** | Balance precisión–exhaustividad | Complementa mAP; controla desbalance |
| **Kappa de Cohen** | Concordancia con ground truth | Reportar κ + Po + IC bootstrap |
| **AUC-ROC macro OVR** | Discriminabilidad | Complementaria; no sustituye mAP |
| CER / WER | Fidelidad de transcripción | Calidad lingüística |
| Latencia, RAM, tamaño | Eficiencia | H2 |
| NASA-TLX / SUS | Carga cognitiva y usabilidad | Variables secundarias |

**Pruebas:** Wilcoxon entre configuraciones, McNemar para decisiones binarias pareadas, bootstrap (5000) para IC y Kappa, criterio de no inferioridad para H2.

---

## 9. Pendientes, riesgos y próximos pasos

### Pendientes `[VERIFICAR]`
- [ ] Umbral de degradación aceptable de mAP con INT8.
- [ ] CER máximo bajo condiciones adversas.
- [ ] Confirmar ambos con la corrida piloto y la literatura.
- [ ] Completar `[Nombre del docente o asesor]` en la portada.
- [ ] Verificar la fecha de portada.

### Riesgos
| Riesgo | Mitigación |
|---|---|
| n = 5 pliegues (poder bajo) | Bootstrap, tamaño del efecto, considerar validación repetida 5×5 |
| AUC-ROC en 63 clases | Explicar como macro one-vs-rest, no binaria |
| Kappa con alta prevalencia | Reportar Po e IC; no interpretar κ aislado |
| Componente pedagógico | Declarado como objetivo 3; confirmar con el asesor |
| Versiones duplicadas del documento | Usar el archivo canónico y este registro |

### Próximos pasos
1. Corrida piloto para fijar umbrales.
2. Revisión del asesor sobre el Encuadre B y los 3 objetivos.
3. Ajuste del Resumen a ≤ 250 palabras (si se exige).
4. Completar protocolo/hardware/versiones definitivas.
5. Validar con el asesor el corpus derivado de 480 imágenes.
6. Entrenar las 4 configuraciones × 5 folds y ejecutar la evaluación.

---

## 10. Inventario de archivos

Estructura por tipo de entregable. Los respaldos y versiones previas se conservan en `04_Respaldos_Historicos/`; no se elimina ningún archivo.

| Archivo | Rol | Notas |
|---|---|---|
| `00_Administrativo/ESTADO_PROYECTO.md` | Seguimiento | Este registro |
| `00_Administrativo/Intrucciones Generales de un proyecto de tesis.txt` | Guía | Rúbrica metodológica |
| `00_Administrativo/Errores Overleaft.md` | Incidencias | Errores de Overleaf y solución aplicada |
| `01_Proyecto_Tesis/Proyecto_OBR_Braille_APA7.docx` | **Canónico** | Versión vigente |
| `01_Proyecto_Tesis/Proyecto_OBR_Braille_Overleaf.pdf` | Exportación | PDF del proyecto desde Overleaf |
| `01_Proyecto_Tesis/Proyecto_OBR_Braille_Overleaf.zip` | Fuente | Código fuente Overleaf; incluye `latexmkrc` (XeLaTeX) |
| `01_Proyecto_Tesis/latexmkrc` | Configuración | Fuerza XeLaTeX en Overleaf |
| `02_Articulo_Cientifico/Articulo_Cientifico_OBR_Braille.docx` | Artículo | Versión editable |
| `02_Articulo_Cientifico/Articulo_OBR_Braille_Overleaf.pdf` | Artículo | Exportación PDF |
| `02_Articulo_Cientifico/Articulo_OBR_Braille_Overleaf.zip` | Fuente | Código fuente Overleaf; incluye `latexmkrc` (XeLaTeX) |
| `02_Articulo_Cientifico/latexmkrc` | Configuración | Fuerza XeLaTeX en Overleaf |
| `03_Evidencias/Evidencia Data.docx` | Evidencia | Registro de datos |
| `03_Evidencias/Avance Proyecto.pdf` | Versión previa | Exportación anterior |
| `04_Respaldos_Historicos/Proyecto_OBR_Braille_APA7_PRE3OBJ.docx` | Respaldo | Antes de reducir a 3 objetivos |
| `04_Respaldos_Historicos/Proyecto_OBR_Braille_APA7_PREENCUADRE.docx` | Respaldo | Antes del Encuadre B |
| `04_Respaldos_Historicos/Proyecto_OBR_Braille_APA7_BACKUP.docx` | Respaldo | Copia de seguridad |
| `04_Respaldos_Historicos/Trabajo Grupo Investigacion.docx` | Versión previa | Estructura anterior |
| `04_Respaldos_Historicos/Trabajo Grupo Investigacion_BACKUP.docx` | Respaldo | Original |
| `04_Respaldos_Historicos/Trabajo Grupo Investigacion_PREAPA.docx` | Respaldo | Antes de APA |
| `04_Respaldos_Historicos/Overleaf_2026-11-12/` | Respaldo | ZIP originales antes de corregir XeLaTeX |
| `05_Plantillas/Plantilla_Proyecto_APA7/` | Plantilla | Proyecto APA 7 editable |
| `05_Plantillas/Plantilla_Proyecto_APA7.zip` | Plantilla | ZIP para Overleaf |
| `05_Plantillas/Plantilla_Articulo_APA7/` | Plantilla | Artículo APA 7 editable |
| `05_Plantillas/Plantilla_Articulo_APA7.zip` | Plantilla | ZIP para Overleaf |
| `05_Plantillas/Ejemplos/` | Ejemplos | Versiones llenas basadas en el trabajo Braille |
| `05_Plantillas/GUIA_Plantillas_APA7.md` | Guía | Uso de las plantillas |
| `05_Plantillas/CHECKLIST_APA7.md` | Checklist | Verificación APA 7 antes de entregar |
| `06_Codigo_Analisis/` | Código | Pipeline de análisis y corpus derivado |
| `06_Codigo_Analisis/PLAN_ACCION_CORPUS_DERIVADO.md` | Plan | Plan aprobado y estado de ejecución |
| `06_Codigo_Analisis/INFORME_AVANCE_2026-11-13.md` | Informe | Avance del análisis de datos, pipeline y resultados |
| `06_Codigo_Analisis/data/processed/derived_480/` | Corpus | 480 imágenes, 40 páginas, 12 condiciones, 63 clases |
| `06_Codigo_Analisis/data/processed/yolo_derived/` | Dataset | YOLO + folds |
| `06_Codigo_Analisis/reports/` | Reportes | Auditoría, validación y figura de condiciones |
| `Semana 5/Proyecto_OBR_Braille_APA7 (1).docx` | **Duplicado** | Fuera de esta carpeta; verificar si está actualizado; **no canónico** |

---

## 11. Checklist de avance

| Sección | Estado |
|---|---|
| Título y portada | ✅ (falta nombre del docente) |
| Resumen y palabras clave | ✅ |
| Planteamiento del problema | ✅ |
| Antecedentes | ✅ |
| Problema general y específicos (3) | ✅ |
| Justificación | ✅ |
| Objetivo general y específicos (3) | ✅ |
| Hipótesis (HG, H0, H1–H3) | ✅ |
| Variables y operacionalización | ✅ |
| Población y muestra | ✅ |
| Metodología (línea, enfoque, tipo, nivel, diseño) | ✅ |
| Métricas (Kappa, AUC-ROC, F1) | ✅ |
| Tablas 1, 2, 3 y A1 | ✅ |
| Limitaciones | ✅ |
| Referencias APA 7 (22) | ✅ |
| Umbrales `[VERIFICAR]` | ⏳ Pendiente |
| Validación del asesor | ⏳ Pendiente |

---

*Registro generado para asegurar la continuidad del proyecto. Actualizar la bitácora y el checklist al cierre de cada sesión.*
