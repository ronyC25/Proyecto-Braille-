import argparse
from pathlib import Path


def export_onnx(weights, imgsz=640, output=None):
    from ultralytics import YOLO

    model = YOLO(weights)
    exported = model.export(format="onnx", imgsz=imgsz, simplify=True, opset=12)
    exported = Path(exported)
    if output:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if exported.resolve() != output.resolve():
            exported.replace(output)
            exported = output
    print(f"ONNX exportado: {exported}")
    return exported


def main():
    parser = argparse.ArgumentParser(description="Exporta un modelo YOLO a ONNX")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    export_onnx(args.weights, args.imgsz, args.output)


if __name__ == "__main__":
    main()
