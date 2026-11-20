import argparse
import json
import time
from pathlib import Path

import numpy as np


def benchmark_onnx(model_path, imgsz=640, runs=50, warmup=5):
    import onnxruntime as ort

    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_meta = session.get_inputs()[0]
    input_name = input_meta.name
    shape = [1, 3, imgsz, imgsz]
    dummy = np.random.rand(*shape).astype(np.float32)
    for _ in range(warmup):
        session.run(None, {input_name: dummy})
    latencies = []
    for _ in range(runs):
        start = time.perf_counter()
        session.run(None, {input_name: dummy})
        latencies.append((time.perf_counter() - start) * 1000)
    size_mb = Path(model_path).stat().st_size / (1024 * 1024)
    result = {
        "model": str(model_path),
        "imgsz": imgsz,
        "runs": runs,
        "latency_ms_mean": float(np.mean(latencies)),
        "latency_ms_p50": float(np.percentile(latencies, 50)),
        "latency_ms_p95": float(np.percentile(latencies, 95)),
        "size_mb": float(size_mb),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Mide latencia y tamaño de un ONNX")
    parser.add_argument("--model", required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--runs", type=int, default=50)
    args = parser.parse_args()
    benchmark_onnx(args.model, args.imgsz, args.runs)


if __name__ == "__main__":
    main()
