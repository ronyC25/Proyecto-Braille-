# Plantilla de Proyecto de Investigación — APA 7

Plantilla reutilizable para proyectos de investigación en LaTeX/Overleaf, con
formato APA 7 y bibliografía automática.

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
main.tex                  Documento principal (no suele necesitar cambios)
config.tex                Datos de portada, resumen, palabras clave y opciones
preamble.tex              Paquetes y formato APA 7
secciones/                Contenido del proyecto, una sección por archivo
referencias.bib           Fuentes en BibTeX/BibLaTeX
figuras/                  Imágenes del proyecto
latexmkrc                 Fuerza XeLaTeX
```

## Qué editar

### 1. Datos del proyecto

Edita `config.tex`: título, autores, filiación, curso, docente, fecha, resumen
y palabras clave.

### 2. Contenido

Cada archivo de `secciones/` corresponde a una sección del proyecto:

| Archivo | Sección |
|---|---|
| `01_planteamiento.tex` | Planteamiento del problema |
| `02_antecedentes.tex` | Antecedentes |
| `03_marco_teorico.tex` | Marco teórico |
| `04_formulacion_problema.tex` | Problema general y específicos |
| `05_justificacion.tex` | Justificación |
| `06_objetivos_hipotesis.tex` | Objetivos e hipótesis |
| `07_variables_operacionalizacion.tex` | Variables y operacionalización |
| `08_poblacion_muestra.tex` | Población y muestra |
| `09_metodologia.tex` | Metodología |
| `10_aspectos_eticos.tex` | Aspectos éticos |
| `11_limitaciones.tex` | Limitaciones |
| `12_apendices.tex` | Apéndices |

Puedes agregar o quitar secciones: crea el archivo y agrega su `\input{...}`
en `main.tex`.

### 3. Referencias

Agrega tus fuentes en `referencias.bib` y cítalas en el texto:

```latex
\parencite{clave}          % (Autor, año)
\textcite{clave}           % Autor (año)
\parencite[p. 12]{clave}   % (Autor, año, p. 12)
```

La lista de referencias se genera sola al final. No escribas la lista a mano.

## Tablas y figuras APA

Tabla:

```latex
\begin{table}[htbp]
  \centering
  \caption{Título de la tabla}
  \label{tab:ejemplo}
  \begin{tabularx}{\textwidth}{@{}lX@{}}
    \toprule
    \textbf{Columna 1} & \textbf{Columna 2} \\
    \midrule
    Dato & Dato \\
    \bottomrule
  \end{tabularx}
  \notaTabla{Fuente: elaboración propia.}
\end{table}
```

Figura:

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\textwidth]{figuras/mi-figura.png}
  \caption{Título de la figura}
  \label{fig:ejemplo}
  \notaFigura{Fuente: elaboración propia.}
\end{figure}
```

## Apéndices

Usa el comando `\apendice{letra}{título}`:

```latex
\apendice{A}{Matriz de consistencia}
```

Las tablas del apéndice se numeran automáticamente como `Tabla A1`, `Tabla A2`.

## Opciones de formato

En `config.tex`:

- `\PortadaProfesionalfalse` → portada de estudiante.
- `\PortadaProfesionaltrue` → portada profesional con running head.
- `\ConIndicetrue` / `\ConIndicetruefalse` → mostrar u omitir el índice.

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
