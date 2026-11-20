# Ejemplo lleno — Artículo Braille

Este ejemplo muestra cómo se ve la plantilla de artículo cuando está completa.
Usa el mismo `preamble.tex`, `articulo.tex` y estructura de `secciones/` que la
plantilla vacía, pero con el contenido condensado del trabajo Braille.

## Qué se llenó

- `config.tex`: título, autores, filiación, resumen y palabras clave.
- `secciones/01` a `05`: introducción, método, resultados esperados, discusión y
  conclusiones.
- `referencias.bib`: 10 fuentes reales del trabajo.

## Nota

El artículo completo está en `02_Articulo_Cientifico/`. Este ejemplo sirve como
referencia de estructura y de uso de las macros APA en dos columnas.

## Cómo compilar

Importa esta carpeta como ZIP en Overleaf. El `latexmkrc` fuerza XeLaTeX y
Overleaf ejecuta Biber automáticamente.
