## AL subir el archivo principal

This compile didn’t produce a PDF. This can happen if:

- There is an unrecoverable LaTeX error. If there are LaTeX errors shown below or in the raw logs, please try to fix them and compile again.
- The `document` environment contains no content. If it’s empty, please add some content and compile again.
- This project contains a file called `output.pdf`. If that file exists, please rename it and compile again.

```
(fontspec)                      LuaTeX.
(fontspec)                      
(fontspec)                      You must change your typesetting engine to,
(fontspec)                      e.g., "xelatex" or "lualatex" instead of
(fontspec)                      "latex" or "pdflatex".

Type <return> to continue.
 ...                                              
                                                  
l.101 \msg_fatal:nn {fontspec} {cannot-use-pdftex}
```

```
<read *> 
         
l.101 \msg_fatal:nn {fontspec} {cannot-use-pdftex}
                                                  
*** (cannot \read from terminal in nonstop modes)
```

## Subir el articulo 

This compile didn’t produce a PDF. This can happen if:

- There is an unrecoverable LaTeX error. If there are LaTeX errors shown below or in the raw logs, please try to fix them and compile again.
- The `document` environment contains no content. If it’s empty, please add some content and compile again.
- This project contains a file called `output.pdf`. If that file exists, please rename it and compile again.

```
(fontspec)                      LuaTeX.
(fontspec)                      
(fontspec)                      You must change your typesetting engine to,
(fontspec)                      e.g., "xelatex" or "lualatex" instead of
(fontspec)                      "latex" or "pdflatex".

Type <return> to continue.
 ...                                              
                                                  
l.101 \msg_fatal:nn {fontspec} {cannot-use-pdftex}
```

```
<read *> 
         
l.101 \msg_fatal:nn {fontspec} {cannot-use-pdftex}
                                                  
*** (cannot \read from terminal in nonstop modes)
```
---

## Solución aplicada (12 de noviembre de 2026)

**Causa:** `main.tex` y `articulo.tex` usan `fontspec` para Times New Roman / TeX Gyre Termes, pero Overleaf compila por defecto con pdfLaTeX. `fontspec` requiere XeLaTeX o LuaLaTeX.

**Corrección en los ZIP:**
- Se agregó `latexmkrc` con `$pdf_mode = 5;` y `$pdflatex = 'xelatex -synctex=1 -interaction=nonstopmode %O %S';` para forzar XeLaTeX automáticamente.
- Se añadió `% !TEX program = xelatex` como primera línea de `main.tex` y `articulo.tex`.
- Se actualizaron los `README.md` de ambos proyectos.
- Respaldos de los ZIP originales en `04_Respaldos_Historicos/Overleaf_2026-11-12/`.

**Si el proyecto ya está creado en Overleaf:** subir el archivo `latexmkrc` a la raíz del proyecto (está disponible junto a cada ZIP) o cambiar manualmente en **Menú → Compiler → XeLaTeX**.