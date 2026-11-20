import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from src.decoding.decode import decode_detections


class OnnxDetector:
    def __init__(self, model_path, imgsz=640, conf=0.25, iou=0.45):
        import onnxruntime as ort

        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou

    def preprocess(self, image):
        height, width = image.shape[:2]
        scale = min(self.imgsz / width, self.imgsz / height)
        new_width = int(round(width * scale))
        new_height = int(round(height * scale))
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((self.imgsz, self.imgsz, 3), 114, dtype=np.uint8)
        pad_x = (self.imgsz - new_width) // 2
        pad_y = (self.imgsz - new_height) // 2
        canvas[pad_y : pad_y + new_height, pad_x : pad_x + new_width] = resized
        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        tensor = rgb.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
        return tensor, scale, pad_x, pad_y

    def _postprocess(self, output, original_shape, scale, pad_x, pad_y):
        prediction = output[0]
        if prediction.ndim == 3:
            prediction = prediction[0]
        if prediction.shape[0] < prediction.shape[1]:
            prediction = prediction.transpose(1, 0)
        boxes_xywh = prediction[:, :4]
        scores = prediction[:, 4:]
        class_ids = scores.argmax(axis=1)
        confidences = scores.max(axis=1)

        keep = confidences >= self.conf
        boxes_xywh = boxes_xywh[keep]
        class_ids = class_ids[keep]
        confidences = confidences[keep]

        detections = []
        original_height, original_width = original_shape
        for class_id in np.unique(class_ids):
            mask = class_ids == class_id
            boxes = boxes_xywh[mask]
            scores_class = confidences[mask]
            xyxy = np.empty_like(boxes)
            xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
            xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
            xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
            xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
            nms_boxes = [
                [float(box[0]), float(box[1]), float(box[2] - box[0]), float(box[3] - box[1])]
                for box in xyxy
            ]
            indices = cv2.dnn.NMSBoxes(
                nms_boxes,
                scores_class.tolist(),
                self.conf,
                self.iou,
            )
            indices = np.array(indices).flatten() if len(indices) else []
            for index in indices:
                x1, y1, x2, y2 = xyxy[index]
                x1 = (x1 - pad_x) / scale
                x2 = (x2 - pad_x) / scale
                y1 = (y1 - pad_y) / scale
                y2 = (y2 - pad_y) / scale
                x1 = max(0.0, min(float(x1), original_width))
                x2 = max(0.0, min(float(x2), original_width))
                y1 = max(0.0, min(float(y1), original_height))
                y2 = max(0.0, min(float(y2), original_height))
                detections.append(
                    {
                        "box": [x1, y1, x2, y2],
                        "class_id": int(class_id),
                        "score": float(scores_class[index]),
                        "x_center": (x1 + x2) / 2 / original_width,
                        "y_center": (y1 + y2) / 2 / original_height,
                    }
                )
        detections.sort(key=lambda item: item["score"], reverse=True)
        return detections

    def detect(self, image):
        tensor, scale, pad_x, pad_y = self.preprocess(image)
        output = self.session.run(None, {self.input_name: tensor})
        return self._postprocess(output, image.shape[:2], scale, pad_x, pad_y)

    def read_text(self, image):
        detections = self.detect(image)
        return decode_detections(detections), detections


def main():
    parser = argparse.ArgumentParser(description="Inferencia ONNX para OBR")
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    detector = OnnxDetector(args.model, args.imgsz, args.conf, args.iou)
    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(args.image)
    text, detections = detector.read_text(image)
    result = {"text": text, "detections": detections}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        Path(args.output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
