# Plantilla de Artículo Científico — APA 7 (2 columnas)

Plantilla reutilizable para artículos científicos compactos en LaTeX/Overleaf,
con citas y referencias APA 7 automáticas.

## Requisitos

- Compilador: **XeLaTeX** (obligatorio por `fontspec`).
- Bibliografía: **Biber**.
- En Overleaf, el archivo `latexmkrc` configura XeLaTeX automáticamente.

## Cómo usarla en Overleaf

1. Descarga el ZIP de la plantilla.
2. En Overleaf: **New Project → Upload Project** y selecciona el ZIP.
3. Espera la compilación. Overleaf ejecutará XeLaTeX y Biber.
4. Si no compila, revisa **Menú → Compiler → XeLaTeX**.

## Estructura

```
articulo.tex              Documento principal (2 columnas)
config.tex                Título, autores, filiación, resumen y palabras clave
preamble.tex              Paquetes y formato del artículo
secciones/                Introducción, método, resultados, discusión, conclusiones
referencias.bib           Fuentes en BibTeX/BibLaTeX
figuras/                  Imágenes del artículo
latexmkrc                 Fuerza XeLaTeX
```

## Qué editar

### 1. Datos del artículo

Edita `config.tex`: título, autores, filiación, resumen y palabras clave.

### 2. Contenido

| Archivo | Sección |
|---|---|
| `01_introduccion.tex` | Introducción, problema, antecedentes, objetivos |
| `02_metodo.tex` | Diseño, muestra, variables y análisis |
| `03_resultados.tex` | Resultados |
| `04_discusion.tex` | Discusión |
| `05_conclusiones.tex` | Conclusiones y limitaciones |

### 3. Referencias

Agrega tus fuentes en `referencias.bib` y cítalas:

```latex
\parencite{clave}          % (Autor, año)
\textcite{clave}           % Autor (año)
\parencite[p. 12]{clave}   % (Autor, año, p. 12)
```

La lista de referencias se genera sola al final.

## Extensión

El artículo está ajustado para ocupar alrededor de **3 páginas**. Si pasa a 4:

- reduce ligeramente el tamaño de fuente en `articulo.tex` (`\fontsize{10.4}{12.4}`),
- reduce los márgenes en `preamble.tex`,
- acorta el resumen o alguna sección.

## Tablas y figuras

Tabla dentro de una columna:

```latex
\begin{table}[H]
  \centering
  \caption{Título de la tabla}
  \label{tab:ejemplo}
  \small
  \begin{tabularx}{\columnwidth}{@{}lX@{}}
    \toprule
    \textbf{Columna 1} & \textbf{Columna 2} \\
    \midrule
    Dato & Dato \\
    \bottomrule
  \end{tabularx}
  \notaTabla{Fuente: elaboración propia.}
\end{table}
```

Figura dentro de una columna:

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=\columnwidth]{figuras/mi-figura.png}
  \caption{Título de la figura}
  \label{fig:ejemplo}
  \notaFigura{Fuente: elaboración propia.}
\end{figure}
```

## Problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `fontspec ... cannot-use-pdftex` | Se compiló con pdfLaTeX | Usar XeLaTeX (`latexmkrc` lo configura) |
| Citas sin resolver | Biber no se ejecutó | Recompilar; en Overleaf es automático |
| `Citation 'x' undefined` | La clave no está en `referencias.bib` | Revisar la clave |
| Acentos rotos | Codificación incorrecta | Guardar los `.tex` en UTF-8 |

## Nota

Esta plantilla es una guía de formato. Verifica siempre las indicaciones
específicas de tu curso, revista o asesor.
