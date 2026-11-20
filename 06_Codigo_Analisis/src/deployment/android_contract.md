# Contrato de integración para la App Android

## Modelo

- Formato recomendado: **ONNX** (ONNX Runtime Mobile) o **TFLite**.
- Entrada: `float32[1, 3, 640, 640]`, RGB, normalizada a `[0, 1]`.
- Preprocesamiento: letterbox con escala uniforme y relleno gris `114`.
- Salida: tensor de detección estilo YOLO. El pipeline de Python acepta
  `(1, 4+63, N)` y `(1, N, 4+63)`.
- Clases: 63 patrones de puntos; `class_id = int_label - 1`.
- `class_id + 1` produce el entero Braille `1..63`.

## Postprocesamiento

1. Filtrar por confianza (`conf >= 0.25` sugerido).
2. Aplicar NMS por clase (`iou = 0.45` sugerido).
3. Convertir cajas de letterbox a coordenadas de la imagen original.
4. Ordenar por líneas: agrupar por `y_center` con tolerancia y ordenar por
   `x_center`.
5. Decodificar cada celda con el mapa español Grado 1.

## JSON de salida

```json
{
  "text": "texto reconocido",
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "class_id": 0,
      "score": 0.98,
      "x_center": 0.12,
      "y_center": 0.34
    }
  ]
}
```

## Requisitos de despliegue

- Latencia objetivo: `< 150 ms` por imagen en gama media/baja.
- Tamaño objetivo: `<= 5 MB` para el modelo cuantizado.
- Memoria objetivo: `<= 150 MB`.
- Ejecución sin conexión.

## Estado

- `src/deployment/infer.py` implementa el contrato en Python con ONNX Runtime.
- `src/training/export_onnx.py` exporta el modelo.
- `src/training/quantize_int8.py` implementa cuantización dinámica INT8.
- **TODO:** cuantización estática con calibración y empaquetado Android.
