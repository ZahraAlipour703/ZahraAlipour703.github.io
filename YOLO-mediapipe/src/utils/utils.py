"""
utils.py
========

General utility functions used throughout the project.

Responsibilities
----------------
- Image loading
- Video loading
- Directory management
- FPS calculation
- Coordinate conversions
- Bounding box utilities
- Saving images
- Saving CSV files

Author
------
Zahra Alipour
"""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import cv2
import numpy as np


# =============================================================================
# Files
# =============================================================================


def create_directory(directory: str | Path) -> Path:
    """
    Create a directory if it does not already exist.

    Parameters
    ----------
    directory : str | Path

    Returns
    -------
    Path
    """

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    return directory


# =============================================================================
# Image Utilities
# =============================================================================


def load_image(path: str | Path) -> np.ndarray:
    """
    Load image from disk.

    Raises
    ------
    FileNotFoundError
    """

    image = cv2.imread(str(path))

    if image is None:
        raise FileNotFoundError(path)

    return image


def save_image(
    image: np.ndarray,
    filename: str,
) -> None:
    """
    Save image to disk.
    """

    create_directory(Path(filename).parent)

    cv2.imwrite(filename, image)


# =============================================================================
# Video Utilities
# =============================================================================


def open_video(
    source: int | str,
) -> cv2.VideoCapture:
    """
    Open webcam or video file.

    Parameters
    ----------
    source
        Webcam ID or filename.
    """

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {source}")

    return cap


# =============================================================================
# Bounding Boxes
# =============================================================================


def clip_bbox(
    bbox: Sequence[int],
    width: int,
    height: int,
) -> Tuple[int, int, int, int]:
    """
    Clip bounding box to image size.
    """

    x1, y1, x2, y2 = bbox

    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(0, min(width - 1, x2))
    y2 = max(0, min(height - 1, y2))

    return x1, y1, x2, y2


def bbox_center(
    bbox: Sequence[int],
) -> Tuple[int, int]:
    """
    Compute bounding box center.
    """

    x1, y1, x2, y2 = bbox

    return (
        (x1 + x2) // 2,
        (y1 + y2) // 2,
    )


# =============================================================================
# Geometry
# =============================================================================


def euclidean_distance(
    p1: Sequence[float],
    p2: Sequence[float],
) -> float:
    """
    Compute Euclidean distance.
    """

    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def midpoint(
    p1: Sequence[int],
    p2: Sequence[int],
) -> Tuple[int, int]:
    """
    Midpoint of two points.
    """

    return (
        (p1[0] + p2[0]) // 2,
        (p1[1] + p2[1]) // 2,
    )


# =============================================================================
# FPS Counter
# =============================================================================


class FPSCounter:
    """
    Real-time FPS calculator.
    """

    def __init__(self) -> None:

        self.previous_time = time.time()
        self.current_fps = 0.0

    def update(self) -> float:
        """
        Update FPS.
        """

        current_time = time.time()

        delta = current_time - self.previous_time

        if delta > 0:
            self.current_fps = 1.0 / delta

        self.previous_time = current_time

        return self.current_fps


# =============================================================================
# CSV Utilities
# =============================================================================


def save_csv(
    filename: str,
    header: List[str],
    rows: Iterable,
) -> None:
    """
    Save iterable rows into CSV.
    """

    create_directory(Path(filename).parent)

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(header)

        writer.writerows(rows)


# =============================================================================
# Drawing
# =============================================================================


def draw_fps(
    frame: np.ndarray,
    fps: float,
) -> np.ndarray:
    """
    Draw FPS on frame.
    """

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    return frame


# =============================================================================
# Colors
# =============================================================================


RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)