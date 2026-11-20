# Datos

## Fuentes utilizadas

| Fuente | Ruta | Páginas | Cajas | Clases |
|---|---|---:|---:|---:|
| Angelina | `../../Semana 7/dataset/data 1/AngelinaDataset` | 334 | 85,263 | 62/63 |
| DSBI `+recto` | `../../Semana 7/dataset/data 2/DSBI` | 110 válidas | 45,627 | 63/63 |

## Angelina

| Subconjunto | Imágenes | Cajas |
|---|---:|---:|
| books | 212 | 66,133 |
| handwritten | 28 | 6,117 |
| not_braille | 44 | 0 |
| uploaded | 50 | 13,013 |

- 44 CSV vacíos corresponden a `not_braille` (negativos).
- Falta la clase 41; DSBI la cubre.
- Desbalance: mínimo 2 cajas, máximo 7,472.
- Commit: `e13038d` (2023-06-05).

## DSBI

- 114 imágenes `+recto`; 110 con anotación válida.
- 4 TXT `+recto` vacíos: `FM+14`, `M+2`, `SVNGCB1+2`, `SVNGCB2+2`.
- 2 TXT no estándar: `M+7-??.txt`, `M+9-??.txt` (texto, no rejilla).
- 63/63 clases; 45,627 cajas en recto.
- Desbalance: mínimo 168, máximo 4,287.
- Commit: `6937eb8` (2018-12-19).

## Exclusiones

- `pics/` de Angelina.
- `figures/` de DSBI.
- `+verso` de DSBI.
- `not_braille` para las 40 páginas del corpus derivado (puede usarse como
  negativos en entrenamiento).
- TXT vacíos y no estándar de DSBI.

## Corpus derivado

| Métrica | Valor |
|---|---:|
| Imágenes | 480 |
| Páginas | 40 |
| Condiciones por página | 12 |
| Cajas | 141,444 |
| Cajas por imagen | 32–598 (promedio 294.7) |
| Clases | 63 |
| Tamaño de imágenes | 1024×1024 |
| Tamaño en disco | 81.9 MB |

### Composición de páginas

| Fuente | Páginas |
|---|---:|
| Angelina books | 20 |
| Angelina uploaded | 5 |
| DSBI recto | 10 |
| Angelina handwritten | 5 |
| **Total** | **40** |

### Folds

| Fold | Imágenes |
|---|---:|
| 0 | 84 |
| 1 | 84 |
| 2 | 84 |
| 3 | 84 |
| 4 | 84 |
| Externo (`-1`) | 60 |

Cada fold controlado tiene 24 páginas de entrenamiento, 4 de validación y 7 de
prueba; las 5 manuscritas son prueba externa.
