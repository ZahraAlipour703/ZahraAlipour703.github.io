"""
Unit tests for src.detection.detector.

These tests avoid requiring real model weights or a GPU: they test the
data structures and pure-drawing logic directly, rather than running
YOLO inference.

Run with:
    pytest tests/test_detector.py
"""

import numpy as np

from src.detection.detector import Detection, YOLODetector


def test_detection_dataclass_defaults():
    det = Detection(bbox=[10, 20, 30, 40], confidence=0.9)

    assert det.bbox == [10, 20, 30, 40]
    assert det.confidence == 0.9
    assert det.class_name == "hand"  # default


def test_draw_renders_without_error_and_returns_same_shape():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    detections = [Detection(bbox=[10, 10, 50, 50], confidence=0.82, class_name="hand")]

    # YOLODetector.draw() is a plain method (doesn't need self.model),
    # so we can call it on an uninitialized instance via __new__ to
    # avoid loading real weights.
    detector = YOLODetector.__new__(YOLODetector)
    output = detector.draw(frame, detections)

    assert output.shape == frame.shape
    # draw() must not mutate the input frame in place
    assert not np.array_equal(output, frame) or len(detections) == 0
