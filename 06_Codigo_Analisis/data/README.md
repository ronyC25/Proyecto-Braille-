# Datos

Los datasets crudos **no se copian** en este proyecto. Se leen desde:

- `../../Semana 7/dataset/data 1/AngelinaDataset`
- `../../Semana 7/dataset/data 2/DSBI`

Las rutas se configuran en `configs/paths.yaml`.

## Salidas generadas

- `interim/pages/`: cajas por página en JSON.
- `processed/derived_480/`: 480 imágenes + etiquetas + metadata.
- `processed/yolo_derived/`: dataset YOLO y folds.
- `splits/`: catálogo y folds.

## Regla

No modificar los datasets originales. Todo cambio se escribe en `data/interim`,
`data/processed` o `data/splits`.
