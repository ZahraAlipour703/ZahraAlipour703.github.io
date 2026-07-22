"""
preprocessing.py
================

Image and Video Preprocessing Module

Responsibilities
----------------
• Read images/videos
• Resize frames
• Normalize images
• Color conversions
• CLAHE enhancement
• ROI cropping
• Video writer utilities

Author
------
Zahra Alipour
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator, Optional, Tuple

import cv2
import numpy as np


class FrameProcessor:
    """
    Handles all preprocessing operations before inference.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] | None = None,
        use_clahe: bool = False,
    ) -> None:

        self.target_size = target_size
        self.use_clahe = use_clahe

        if use_clahe:
            self.clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8),
            )

    # ---------------------------------------------------------

    def resize(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Resize frame while preserving aspect ratio.
        """

        if self.target_size is None:
            return frame

        return cv2.resize(
            frame,
            self.target_size,
            interpolation=cv2.INTER_LINEAR,
        )

    # ---------------------------------------------------------

    def bgr_to_rgb(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Convert BGR to RGB.
        """

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ---------------------------------------------------------

    def rgb_to_bgr(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Convert RGB to BGR.
        """

        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # ---------------------------------------------------------

    def normalize(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize image to [0,1].
        """

        return frame.astype(np.float32) / 255.0

    # ---------------------------------------------------------

    def denormalize(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Convert normalized image back to uint8.
        """

        frame = np.clip(frame * 255, 0, 255)

        return frame.astype(np.uint8)

    # ---------------------------------------------------------

    def enhance_contrast(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Apply CLAHE contrast enhancement.
        """

        if not self.use_clahe:
            return frame

        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        l, a, b = cv2.split(lab)

        l = self.clahe.apply(l)

        enhanced = cv2.merge((l, a, b))

        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # ---------------------------------------------------------

    def crop_roi(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
    ) -> np.ndarray:
        """
        Crop bounding box region.
        """

        x1, y1, x2, y2 = bbox

        h, w = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(w, x2)
        y2 = min(h, y2)

        return frame[y1:y2, x1:x2]

    # ---------------------------------------------------------

    def preprocess(
        self,
        frame: np.ndarray,
    ) -> np.ndarray:
        """
        Complete preprocessing pipeline.
        """

        frame = self.resize(frame)

        frame = self.enhance_contrast(frame)

        return frame


# ======================================================================


class VideoReader:
    """
    Reads video frame-by-frame.
    """

    def __init__(self, source: str | int):

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open source: {source}")

    # ---------------------------------------------------------

    def frames(self) -> Generator[np.ndarray, None, None]:
        """
        Generator returning video frames.
        """

        while True:

            success, frame = self.cap.read()

            if not success:
                break

            yield frame

    # ---------------------------------------------------------

    def release(self):

        self.cap.release()


# ======================================================================


class VideoWriter:
    """
    Saves processed videos.
    """

    def __init__(
        self,
        output_path: str,
        fps: float,
        frame_size: Tuple[int, int],
    ) -> None:

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            frame_size,
        )

    # ---------------------------------------------------------

    def write(
        self,
        frame: np.ndarray,
    ) -> None:

        self.writer.write(frame)

    # ---------------------------------------------------------

    def release(self):

        self.writer.release()


# ======================================================================


def load_image(path: str) -> np.ndarray:
    """
    Load image from disk.
    """

    image = cv2.imread(path)

    if image is None:
        raise FileNotFoundError(path)

    return image


def save_image(
    path: str,
    image: np.ndarray,
) -> None:
    """
    Save image.
    """

    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(path, image)