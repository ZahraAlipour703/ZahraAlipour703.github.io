"""
visualization.py
================

Visualization utilities for the complete hand tracking pipeline.

Responsibilities
----------------
• Draw YOLO detections
• Draw MediaPipe landmarks
• Draw ArUco markers
• Draw joint angles
• Draw FPS
• Draw segmentation masks
• Draw information panels

Author:
    Zahra Alipour
"""

from __future__ import annotations

from typing import Dict, List, Optional

import cv2
import mediapipe as mp
import numpy as np

from src.detection.detector import Detection
from src.tracking.mediapipe_tracker import HandLandmarks
from src.tracking.aruco_tracker import MarkerPose


class Visualizer:
    """
    Draws all outputs of the tracking pipeline.

    This class performs no calculations.
    It only renders results produced by other modules.
    """

    def __init__(self):

        self.drawer = mp.solutions.drawing_utils

        self.hand_connections = mp.solutions.hands.HAND_CONNECTIONS

    # ---------------------------------------------------------

    def draw_yolo(
        self,
        image: np.ndarray,
        detections: List[Detection],
    ) -> np.ndarray:
        """
        Draw YOLO bounding boxes.
        """

        output = image.copy()

        for det in detections:

            x1, y1, x2, y2 = det.bbox

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                output,
                f"{det.class_name} {det.confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return output

    # ---------------------------------------------------------

    def draw_landmarks(
        self,
        image: np.ndarray,
        hands: List[HandLandmarks],
    ) -> np.ndarray:
        """
        Draw MediaPipe landmarks.
        """

        output = image.copy()

        for hand in hands:

            for point in hand.landmarks:

                cv2.circle(
                    output,
                    point,
                    4,
                    (0, 0, 255),
                    -1,
                )

            for connection in self.hand_connections:

                p1 = hand.landmarks[connection[0]]
                p2 = hand.landmarks[connection[1]]

                cv2.line(
                    output,
                    p1,
                    p2,
                    (255, 0, 255),
                    2,
                )

        return output

    # ---------------------------------------------------------

    def draw_aruco(
        self,
        image: np.ndarray,
        poses: List[MarkerPose],
        camera_matrix: np.ndarray,
        distortion: np.ndarray,
        marker_length: float,
    ) -> np.ndarray:
        """
        Draw ArUco markers.
        """

        output = image.copy()

        for pose in poses:

            cv2.polylines(
                output,
                [pose.corners.astype(np.int32)],
                True,
                (255, 255, 0),
                2,
            )

            cv2.drawFrameAxes(
                output,
                camera_matrix,
                distortion,
                pose.rvec,
                pose.tvec,
                marker_length,
            )

        return output

    # ---------------------------------------------------------

    def draw_angles(
        self,
        image: np.ndarray,
        angles: Optional[Dict[str, float]],
    ) -> np.ndarray:
        """
        Display joint angles.
        """

        if angles is None:

            return image

        output = image.copy()

        y = 30

        for name, value in angles.items():

            cv2.putText(
                output,
                f"{name}: {value:.1f}°",
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            y += 30

        return output

    # ---------------------------------------------------------

    def draw_fps(
        self,
        image: np.ndarray,
        fps: float,
    ) -> np.ndarray:
        """
        Draw FPS counter.
        """

        output = image.copy()

        cv2.putText(
            output,
            f"FPS : {fps:.1f}",
            (20, output.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        return output

    # ---------------------------------------------------------

    def draw_mask(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray],
        alpha: float = 0.5,
    ) -> np.ndarray:
        """
        Overlay segmentation mask.
        """

        if mask is None:

            return image

        output = image.copy()

        colored = np.zeros_like(output)

        colored[:, :, 1] = mask * 255

        return cv2.addWeighted(
            output,
            1 - alpha,
            colored,
            alpha,
            0,
        )

    # ---------------------------------------------------------

    def draw_pipeline(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        hands: List[HandLandmarks],
        poses: List[MarkerPose],
        angles: Optional[Dict[str, float]],
        fps: float,
        camera_matrix: Optional[np.ndarray] = None,
        distortion: Optional[np.ndarray] = None,
        marker_length: float = 0.02,
        mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Draw the complete pipeline output.
        """

        image = frame.copy()

        image = self.draw_yolo(image, detections)

        image = self.draw_landmarks(image, hands)

        if camera_matrix is not None and distortion is not None:

            image = self.draw_aruco(
                image,
                poses,
                camera_matrix,
                distortion,
                marker_length,
            )

        image = self.draw_angles(image, angles)

        image = self.draw_fps(image, fps)

        image = self.draw_mask(image, mask)

        return image