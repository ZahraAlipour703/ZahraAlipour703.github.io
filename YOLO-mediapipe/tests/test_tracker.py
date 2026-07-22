"""
Unit tests for src.tracking.tracker.HandTracker.

Uses lightweight fake detector/landmark-tracker objects that implement
the same interface as YOLODetector/MediaPipeTracker, so these tests
don't require real model weights.

Run with:
    pytest tests/test_tracker.py
"""

import numpy as np

from src.detection.detector import Detection
from src.geometry.angle_calculator import AngleCalculator
from src.tracking.mediapipe_tracker import HandLandmarks
from src.tracking.tracker import HandTracker, TrackingResult


class FakeDetector:
    def detect(self, frame):
        return [Detection(bbox=[0, 0, 50, 50], confidence=0.99, class_name="hand")]


class FakeLandmarkTracker:
    def process(self, frame, boxes):
        # 21 landmarks in a straight vertical line per finger segment,
        # just enough for AngleCalculator to run without error.
        landmarks = [(0, -i) for i in range(21)]
        return [HandLandmarks(bbox=boxes[0], landmarks=landmarks, handedness="Right", score=0.95)]


def test_process_returns_tracking_result_with_expected_shape():
    tracker = HandTracker(
        detector=FakeDetector(),
        landmark_tracker=FakeLandmarkTracker(),
        angle_calculator=AngleCalculator(),
    )

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = tracker.process(frame)

    assert isinstance(result, TrackingResult)
    assert len(result.detections) == 1
    assert len(result.hands) == 1
    assert result.angles is not None
    assert "index_pip" in result.angles
    assert result.fps > 0


def test_process_with_no_hands_detected_returns_none_angles():
    class EmptyLandmarkTracker:
        def process(self, frame, boxes):
            return []

    tracker = HandTracker(
        detector=FakeDetector(),
        landmark_tracker=EmptyLandmarkTracker(),
        angle_calculator=AngleCalculator(),
    )

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    result = tracker.process(frame)

    assert result.hands == []
    assert result.angles is None
