# Preparación para la App

## Pipeline

```
Imagen → letterbox 640 → YOLO ONNX → NMS → orden de lectura → decodificación Braille → texto
```

## Exportación

```bash
python -m src.training.export_onnx \
  --weights outputs/runs/yolov8n_fp32/weights/best.pt \
  --output outputs/models/yolov8n_fp32.onnx
```

## Cuantización INT8

```bash
python -m src.training.quantize_int8 \
  --input outputs/models/yolov8n_fp32.onnx \
  --output outputs/models/yolov8n_int8.onnx
```

Estado: cuantización **dinámica** de pesos implementada. La cuantización
**estática** con `CalibrationDataReader` queda como `TODO`.

## Inferencia

```bash
python -m src.deployment.infer \
  --model outputs/models/yolov8n_int8.onnx \
  --image ruta/a/imagen.jpg \
  --output salida.json
```

## Contrato Android

Ver `src/deployment/android_contract.md`.

Resumen:

- Entrada `float32[1, 3, 640, 640]`, RGB, `[0, 1]`.
- Salida YOLO con 63 clases.
- `class_id + 1` = patrón Braille `1..63`.
- NMS por clase, `conf=0.25`, `iou=0.45`.
- JSON con `text` y `detections`.
- Objetivos: `<150 ms`, `<=5 MB`, `<=150 MB` RAM.

## Pendientes

- Cuantización estática con calibración.
- Empaquetado Android (ONNX Runtime Mobile o TFLite).
- Mapa español completo (acentos, `¿`, `¡`, `«`, `»`, números, mayúsculas).
- Pruebas en dispositivo de gama media/baja.
