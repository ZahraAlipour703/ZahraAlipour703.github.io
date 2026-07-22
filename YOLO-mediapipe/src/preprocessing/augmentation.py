"""
augmentation.py
===============

Data augmentation utilities for the YOLO + MediaPipe Hand Tracking project.

This module provides image augmentation pipelines for training,
validation, and test-time augmentation (TTA).

Features
--------
• Training augmentations
• Validation pipeline
• Test pipeline
• Test-Time Augmentation (TTA)
• Custom augmentation interface
• Bounding-box aware transformations (YOLO format)

Author
------
Zahra Alipour
"""

from __future__ import annotations

from typing import List, Tuple

import albumentations as A
import cv2
import numpy as np


class DataAugmentation:
    """
    Image augmentation pipeline using Albumentations.

    Supports YOLO bounding boxes.

    Example
    -------
    >>> aug = DataAugmentation()
    >>> img, boxes, labels = aug.train(image, boxes, labels)
    """

    def __init__(self) -> None:

        # ------------------------------------------------------------
        # Training pipeline
        # ------------------------------------------------------------

        self.train_transform = A.Compose(
            [

                # Geometry
                A.HorizontalFlip(p=0.5),

                A.Rotate(
                    limit=20,
                    border_mode=cv2.BORDER_CONSTANT,
                    p=0.4,
                ),

                A.RandomScale(
                    scale_limit=0.15,
                    p=0.4,
                ),

                A.ShiftScaleRotate(
                    shift_limit=0.05,
                    scale_limit=0.05,
                    rotate_limit=10,
                    border_mode=cv2.BORDER_CONSTANT,
                    p=0.3,
                ),

                # Brightness / Contrast

                A.RandomBrightnessContrast(
                    brightness_limit=0.2,
                    contrast_limit=0.2,
                    p=0.5,
                ),

                # HSV

                A.HueSaturationValue(
                    hue_shift_limit=10,
                    sat_shift_limit=15,
                    val_shift_limit=10,
                    p=0.4,
                ),

                # Blur

                A.GaussianBlur(
                    blur_limit=(3, 5),
                    p=0.2,
                ),

                A.MotionBlur(
                    blur_limit=5,
                    p=0.15,
                ),

                # Noise

                A.GaussNoise(
                    p=0.2,
                ),

                # CLAHE

                A.CLAHE(
                    clip_limit=2.0,
                    p=0.3,
                ),

                # Compression

                A.ImageCompression(
                    quality_range=(80, 100),
                    p=0.2,
                ),

            ],
            bbox_params=A.BboxParams(
                format="yolo",
                label_fields=["class_labels"],
            ),
        )

        # ------------------------------------------------------------
        # Validation pipeline
        # ------------------------------------------------------------

        self.validation_transform = A.Compose(
            [],
            bbox_params=A.BboxParams(
                format="yolo",
                label_fields=["class_labels"],
            ),
        )

        # ------------------------------------------------------------
        # Test pipeline
        # ------------------------------------------------------------

        self.test_transform = A.Compose(
            [],
            bbox_params=A.BboxParams(
                format="yolo",
                label_fields=["class_labels"],
            ),
        )

    # ============================================================

    def train(
        self,
        image: np.ndarray,
        boxes: List[List[float]],
        labels: List[int],
    ) -> Tuple[np.ndarray, List[List[float]], List[int]]:
        """
        Apply training augmentation.
        """

        transformed = self.train_transform(
            image=image,
            bboxes=boxes,
            class_labels=labels,
        )

        return (
            transformed["image"],
            transformed["bboxes"],
            transformed["class_labels"],
        )

    # ============================================================

    def validate(
        self,
        image: np.ndarray,
        boxes: List[List[float]],
        labels: List[int],
    ):

        transformed = self.validation_transform(
            image=image,
            bboxes=boxes,
            class_labels=labels,
        )

        return (
            transformed["image"],
            transformed["bboxes"],
            transformed["class_labels"],
        )

    # ============================================================

    def test(
        self,
        image: np.ndarray,
        boxes: List[List[float]],
        labels: List[int],
    ):

        transformed = self.test_transform(
            image=image,
            bboxes=boxes,
            class_labels=labels,
        )

        return (
            transformed["image"],
            transformed["bboxes"],
            transformed["class_labels"],
        )

    # ============================================================

    def tta(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Test-Time Augmentation (TTA).

        Returns multiple augmented copies of an image.

        Useful for robust inference.
        """

        augmentations = [

            image,

            cv2.flip(image, 1),

            cv2.rotate(
                image,
                cv2.ROTATE_90_CLOCKWISE,
            ),

            cv2.rotate(
                image,
                cv2.ROTATE_90_COUNTERCLOCKWISE,
            ),

            cv2.GaussianBlur(
                image,
                (3, 3),
                0,
            ),

        ]

        return augmentations


# ======================================================================


def visualize(
    image: np.ndarray,
    augmented: np.ndarray,
) -> np.ndarray:
    """
    Display original and augmented image side by side.
    """

    return np.hstack((image, augmented))