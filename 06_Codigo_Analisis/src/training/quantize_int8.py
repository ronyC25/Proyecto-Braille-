import argparse
from pathlib import Path


def quantize_dynamic_int8(input_path, output_path):
    """Cuantización dinámica INT8 de pesos (punto de partida para la App).

    TODO: implementar cuantización estática con un CalibrationDataReader usando
    imágenes del split de validación, que es la variante que evaluará H2.
    """
    from onnxruntime.quantization import QuantType, quantize_dynamic

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quantize_dynamic(
        str(input_path),
        str(output_path),
        weight_type=QuantType.QInt8,
    )
    print(f"Modelo INT8 (dinámico) generado: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Cuantiza un ONNX a INT8")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    quantize_dynamic_int8(args.input, args.output)


if __name__ == "__main__":
    main()
