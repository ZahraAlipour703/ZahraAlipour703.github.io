"""
tracker.py
==========

High-level tracking pipeline.

This module combines:

    • YOLO hand detection
    • MediaPipe landmark estimation
    • Temporal tracking
    • Angle calculation

It is responsible for processing one video frame and
returning all information required by the visualization
module.

Author:
    Zahra Alipour
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import time

import cv2
import numpy as np

from src.detection.detector import YOLODetector, Detection
from src.tracking.mediapipe_tracker import (
    MediaPipeTracker,
    HandLandmarks,
)
from src.geometry.angle_calculator import AngleCalculator


# ---------------------------------------------------------
# Data Structure
# ---------------------------------------------------------


@dataclass
class TrackingResult:
    """
    Stores the result of one processed frame.
    """

    frame: np.ndarray

    detections: List[Detection]

    hands: List[HandLandmarks]

    angles: Optional[dict]

    fps: float


# ---------------------------------------------------------
# Tracker
# ---------------------------------------------------------


class HandTracker:
    """
    Complete Hand Tracking Pipeline.

    Pipeline

        Frame
          │
          ▼
        YOLO
          │
          ▼
      Bounding Boxes
          │
          ▼
      MediaPipe Hands
          │
          ▼
       21 Landmarks
          │
          ▼
     Joint Angle Calculation
          │
          ▼
      Tracking Result
    """

    def __init__(
        self,
        detector: YOLODetector,
        landmark_tracker: MediaPipeTracker,
        angle_calculator: Optional[AngleCalculator] = None,
    ) -> None:

        self.detector = detector

        self.landmark_tracker = landmark_tracker

        self.angle_calculator = angle_calculator

        self.previous_time = time.time()

    # -----------------------------------------------------

    def process(
        self,
        frame: np.ndarray,
    ) -> TrackingResult:
        """
        Process one frame.

        Parameters
        ----------
        frame
            Input BGR image.

        Returns
        -------
        TrackingResult
        """

        detections = self.detector.detect(frame)

        boxes = []

        for det in detections:

            boxes.append(det.bbox)

        hands = self.landmark_tracker.process(
            frame,
            boxes,
        )

        angles = None

        if self.angle_calculator is not None and hands:

            # Visualizer.draw_angles() expects a single flat
            # {name: value} dict, so we report the first tracked
            # hand's angles (matches the default max_num_hands=1).
            joint_angles = self.angle_calculator.compute_from_landmarks(
                hands[0].landmarks
            )
            angles = self.angle_calculator.to_dictionary(joint_angles)

        current = time.time()

        fps = 1.0 / max(current - self.previous_time, 1e-6)

        self.previous_time = current

        return TrackingResult(

            frame=frame,

            detections=detections,

            hands=hands,

            angles=angles,

            fps=fps,

        )

    # -----------------------------------------------------

    def draw(
        self,
        result: TrackingResult,
    ) -> np.ndarray:
        """
        Draw all tracking information.

        Parameters
        ----------
        result

        Returns
        -------
        Annotated frame.
        """

        image = result.frame.copy()

        image = self.landmark_tracker.draw(
            image,
            result.hands,
        )

        cv2.putText(

            image,

            f"FPS : {result.fps:.1f}",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 255, 0),

            2,

        )

        return image

    # -----------------------------------------------------

    def process_video(
        self,
        source: int | str = 0,
    ) -> None:
        """
        Run real-time tracking.

        Parameters
        ----------
        source

            Webcam index or video path.
        """

        cap = cv2.VideoCapture(source)

        if not cap.isOpened():

            raise RuntimeError(
                f"Cannot open video source: {source}"
            )

        while True:

            success, frame = cap.read()

            if not success:

                break

            result = self.process(frame)

            output = self.draw(result)

            cv2.imshow(
                "YOLO + MediaPipe Tracking",
                output,
            )

            key = cv2.waitKey(1)

            if key == ord("q"):

                break

        cap.release()

        cv2.destroyAllWindows()