# Guía general de plantillas APA 7

Este paquete contiene dos plantillas reutilizables para Overleaf:

| Plantilla | Uso | Formato |
|---|---|---|
| `Plantilla_Proyecto_APA7` | Proyecto o protocolo de investigación | 1 columna, doble espacio, 12 pt |
| `Plantilla_Articulo_APA7` | Artículo científico | 2 columnas, ~3 páginas, 10.4 pt |

Ambas incluyen:

- Formato APA 7 (Times New Roman o TeX Gyre Termes, márgenes de 2.54 cm,
  interlineado y títulos).
- Portada, resumen y palabras clave.
- Citas y referencias automáticas con `biblatex-apa` + `biber`.
- Tablas y figuras con numeración y notas APA.
- Apéndices con tablas A1, A2, etc. (plantilla de proyecto).
- `latexmkrc` para compilar con XeLaTeX sin configuración manual.
- Ejemplos llenos en `Ejemplos/`.

## Flujo de trabajo recomendado

1. Elige la plantilla según el entregable.
2. Descarga su ZIP e impórtalo en Overleaf:
   **New Project → Upload Project**.
3. Edita `config.tex` con tus datos.
4. Escribe el contenido en `secciones/`.
5. Agrega tus fuentes en `referencias.bib` y cítalas con
   `\parencite{clave}` o `\textcite{clave}`.
6. Compila. Overleaf ejecuta XeLaTeX y Biber automáticamente.
7. Revisa el `CHECKLIST_APA7.md` antes de entregar.

## Cómo agregar una sección

1. Crea un archivo en `secciones/`, por ejemplo `13_mi_seccion.tex`.
2. Escribe `\section{Mi sección}` y el contenido.
3. Agrega `\input{secciones/13_mi_seccion}` en `main.tex` o `articulo.tex`.

## Cómo cambiar de una columna a dos (o viceversa)

- Proyecto: usa `\documentclass[12pt,a4paper]{article}` y no cargues `multicol`.
- Artículo: usa `\documentclass[10pt,a4paper]{extarticle}` y envuelve el cuerpo
  en `\begin{multicols}{2} ... \end{multicols}`.

## Cómo cambiar el tamaño de página

En `preamble.tex`, cambia `a4paper` por `letterpaper` en la línea de
`\documentclass` y ajusta `geometry` si es necesario.

## Citas APA más usadas

```latex
\parencite{clave}              % (Autor, año)
\textcite{clave}               % Autor (año)
\parencite[p. 12]{clave}       % (Autor, año, p. 12)
\textcite[p. 12]{clave}        % Autor (año, p. 12)
\citeauthor{clave}             % Autor
\citeyear{clave}               % año
```

## Referencias

No escribas la lista de referencias a mano. Agrega las fuentes en
`referencias.bib` y usa `\printbibliography`. biblatex-apa ordena
alfabéticamente y aplica sangría francesa.

## Tablas y figuras

- Tabla: número y título **encima**, nota **debajo**.
- Figura: número y título **encima**, imagen, nota **debajo**.
- Use `\notaTabla{...}` y `\notaFigura{...}`.
- Evite líneas verticales; use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).

## Problemas frecuentes

| Problema | Causa | Solución |
|---|---|---|
| `fontspec ... cannot-use-pdftex` | pdfLaTeX | XeLaTeX (`latexmkrc`) |
| Citas sin resolver | Biber no ejecutado | Recompilar |
| `Citation undefined` | Clave ausente en `.bib` | Revisar clave |
| Acentos rotos | Codificación | Guardar en UTF-8 |
| El artículo pasa a 4 páginas | Exceso de texto | Ajustar fuente, márgenes o resumen |

## Adaptación a una revista o curso

- Revise si la revista exige una clase propia (`.cls`) o un formato distinto.
- Si exige APA 7, conserve `biblatex-apa`; si exige otro estilo, cambie
  `style=apa` por el estilo correspondiente.
- Si exige una portada institucional, reemplace `\PortadaAPA` por la portada
  oficial.

## Nota

Las plantillas son una guía de formato. Siempre prevalece la indicación del
docente, asesor o revista.
