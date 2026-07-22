"""
detector.py
===========

YOLOv8 Hand Detector

This module loads a trained YOLOv8 model and performs hand detection on
images or video frames.

Author: Zahra Alipour
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    """
    One YOLO detection, in the shape expected by
    src.tracking.tracker.HandTracker and
    src.visualization.visualization.Visualizer.
    """

    bbox: List[int]
    confidence: float
    class_name: str = field(default="hand")


class YOLODetector:
    """
    Wrapper around Ultralytics YOLO model.

    Example
    -------
    detector = YOLODetector("models/yolov8n.pt")

    detections = detector.detect(frame)
    """

    def __init__(
        self,
        model_path: str,
        confidence: float = 0.35,
        device: str = "cpu",
    ) -> None:

        self.model_path = Path(model_path)

        # Allow either a local checkpoint or a stock Ultralytics model
        # name (e.g. "yolov8n.pt"), which Ultralytics auto-downloads.
        if not self.model_path.exists() and not str(model_path).endswith(".pt"):
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.confidence = confidence
        self.device = device

        self.model = YOLO(str(model_path))

    # -------------------------------------------------------------

    def detect(
        self,
        frame: np.ndarray,
    ) -> List[Detection]:
        """
        Detect hands.

        Parameters
        ----------
        frame
            OpenCV image (BGR)

        Returns
        -------
        list[Detection]
        """

        prediction = self.model.predict(
            source=frame,
            conf=self.confidence,
            device=self.device,
            verbose=False,
        )

        detections: List[Detection] = []

        if len(prediction) == 0:
            return detections

        result = prediction[0]

        if result.boxes is None:
            return detections

        for box in result.boxes:

            x1, y1, x2, y2 = (
                box.xyxy.cpu().numpy()[0].astype(int)
            )

            conf = float(box.conf.cpu())
            cls_id = int(box.cls.cpu()) if box.cls is not None else 0
            class_name = result.names.get(cls_id, "hand") if hasattr(result, "names") else "hand"

            detections.append(
                Detection(
                    bbox=[int(x1), int(y1), int(x2), int(y2)],
                    confidence=conf,
                    class_name=class_name,
                )
            )

        return detections

    # -------------------------------------------------------------

    def draw(
        self,
        frame: np.ndarray,
        detections: List[Detection],
    ) -> np.ndarray:
        """
        Draw detections on frame.
        """

        image = frame.copy()

        for det in detections:

            x1, y1, x2, y2 = det.bbox

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                image,
                f"{det.class_name} {det.confidence:.2f}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return image

    # -------------------------------------------------------------

    def detect_and_draw(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Convenience function.

        Detect hands and draw bounding boxes.
        """

        detections = self.detect(frame)

        return self.draw(frame, detections)