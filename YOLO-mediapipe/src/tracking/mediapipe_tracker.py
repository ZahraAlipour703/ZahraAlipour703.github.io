"""
mediapipe_tracker.py
====================

MediaPipe Hand Landmark Tracker

Uses YOLO detections as Regions of Interest (ROI) and estimates
21 hand landmarks for each detected hand.

Author: Zahra Alipour
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class HandLandmarks:
    """
    Stores one detected hand.
    """

    bbox: List[int]
    landmarks: List[tuple[int, int]]
    handedness: str
    score: float


class MediaPipeTracker:
    """
    Runs MediaPipe Hands on YOLO detections.

    Workflow
    --------
    YOLO
      ↓
    Bounding Box
      ↓
    Crop ROI
      ↓
    MediaPipe Hands
      ↓
    21 Landmarks
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ) -> None:

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    # ---------------------------------------------------------

    def process(
        self,
        frame: np.ndarray,
        boxes: List[List[int]],
    ) -> List[HandLandmarks]:
        """
        Estimate landmarks for every YOLO detection.

        Parameters
        ----------
        frame
            Original BGR frame.

        boxes
            YOLO bounding boxes.

        Returns
        -------
        list[HandLandmarks]
        """

        results_list: List[HandLandmarks] = []

        height, width = frame.shape[:2]

        for box in boxes:

            x1, y1, x2, y2 = box

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)

            roi = frame[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            result = self.hands.process(rgb)

            if result.multi_hand_landmarks is None:
                continue

            for hand_index, hand_landmarks in enumerate(
                result.multi_hand_landmarks
            ):

                points = []

                roi_h, roi_w = roi.shape[:2]

                for landmark in hand_landmarks.landmark:

                    px = int(landmark.x * roi_w) + x1
                    py = int(landmark.y * roi_h) + y1

                    points.append((px, py))

                handedness = "Unknown"
                confidence = 0.0

                if result.multi_handedness:

                    handedness = (
                        result.multi_handedness[hand_index]
                        .classification[0]
                        .label
                    )

                    confidence = (
                        result.multi_handedness[hand_index]
                        .classification[0]
                        .score
                    )

                results_list.append(
                    HandLandmarks(
                        bbox=box,
                        landmarks=points,
                        handedness=handedness,
                        score=float(confidence),
                    )
                )

        return results_list

    # ---------------------------------------------------------

    def draw(
        self,
        frame: np.ndarray,
        hands: List[HandLandmarks],
    ) -> np.ndarray:
        """
        Draw landmarks on image.
        """

        image = frame.copy()

        for hand in hands:

            for point in hand.landmarks:

                cv2.circle(
                    image,
                    point,
                    3,
                    (0, 0, 255),
                    -1,
                )

            x1, y1, _, _ = hand.bbox

            cv2.putText(
                image,
                f"{hand.handedness} {hand.score:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2,
            )

        return image

    # ---------------------------------------------------------

    def close(self) -> None:
        """
        Release MediaPipe resources.
        """

        self.hands.close()