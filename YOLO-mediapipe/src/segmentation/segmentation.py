"""
segmentation.py
===============

Hand segmentation module.

This file provides a unified interface for generating hand masks after
YOLO detects the hand bounding box.

Supported methods
-----------------
1. Segment Anything Model (SAM)
2. YOLOv8 Segmentation

Author: Zahra Alipour
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

LOGGER = logging.getLogger(__name__)


class HandSegmenter:
    """
    Hand segmentation using SAM or YOLO segmentation.

    Parameters
    ----------
    model_path : str
        Path to segmentation model.
    model_type : str
        "sam" or "yolo".
    """

    def __init__(
        self,
        model_path: str,
        model_type: str = "sam",
    ) -> None:

        self.model_type = model_type.lower()
        self.model_path = Path(model_path)

        self.model = None

        self._load_model()

    ####################################################################
    # Model Loading
    ####################################################################

    def _load_model(self) -> None:
        """
        Load segmentation model.
        """

        if self.model_type == "sam":
            self._load_sam()

        elif self.model_type == "yolo":
            self._load_yolo_seg()

        else:
            raise ValueError(
                f"Unsupported segmentation model: {self.model_type}"
            )

    def _load_sam(self) -> None:
        """
        Load Segment Anything Model.
        """

        try:
            from segment_anything import (
                sam_model_registry,
                SamPredictor,
            )

            sam = sam_model_registry["vit_b"](
                checkpoint=str(self.model_path)
            )

            self.model = SamPredictor(sam)

            LOGGER.info("SAM loaded successfully.")

        except Exception as e:
            LOGGER.error("Unable to load SAM.")
            raise e

    def _load_yolo_seg(self) -> None:
        """
        Load YOLO segmentation model.
        """

        try:
            from ultralytics import YOLO

            self.model = YOLO(str(self.model_path))

            LOGGER.info("YOLO Segmentation model loaded.")

        except Exception as e:
            LOGGER.error("Unable to load YOLO segmentation.")
            raise e

    ####################################################################
    # Public API
    ####################################################################

    def segment(
        self,
        frame: np.ndarray,
        bbox: List[int],
    ) -> Optional[np.ndarray]:
        """
        Generate segmentation mask.

        Parameters
        ----------
        frame : ndarray

        bbox : [x1,y1,x2,y2]

        Returns
        -------
        Binary mask.
        """

        if self.model_type == "sam":
            return self._segment_sam(frame, bbox)

        return self._segment_yolo(frame, bbox)

    ####################################################################
    # SAM
    ####################################################################

    def _segment_sam(
        self,
        frame: np.ndarray,
        bbox: List[int],
    ) -> Optional[np.ndarray]:

        x1, y1, x2, y2 = bbox

        self.model.set_image(frame)

        masks, scores, _ = self.model.predict(
            box=np.array([x1, y1, x2, y2]),
            multimask_output=False,
        )

        if len(masks) == 0:
            return None

        return masks[0].astype(np.uint8)

    ####################################################################
    # YOLO Segmentation
    ####################################################################

    def _segment_yolo(
        self,
        frame: np.ndarray,
    ) -> Optional[np.ndarray]:

        results = self.model.predict(
            frame,
            verbose=False,
        )

        if len(results) == 0:
            return None

        result = results[0]

        if result.masks is None:
            return None

        return result.masks.data[0].cpu().numpy().astype(np.uint8)

    ####################################################################
    # Utilities
    ####################################################################

    @staticmethod
    def apply_mask(
        frame: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """
        Overlay segmentation mask.

        Parameters
        ----------
        frame : ndarray

        mask : ndarray

        Returns
        -------
        Segmented image.
        """

        colored = np.zeros_like(frame)

        colored[:, :, 1] = mask * 255

        return cv2.addWeighted(
            frame,
            0.75,
            colored,
            0.25,
            0,
        )

    @staticmethod
    def crop_mask(
        frame: np.ndarray,
        mask: np.ndarray,
    ) -> np.ndarray:
        """
        Return cropped hand.

        Parameters
        ----------
        frame : ndarray

        mask : ndarray

        Returns
        -------
        Cropped RGB image.
        """

        return cv2.bitwise_and(
            frame,
            frame,
            mask=mask.astype(np.uint8),
        )


def build_segmenter(
    model_path: str,
    model_type: str = "sam",
) -> HandSegmenter:
    """
    Factory function.

    Returns
    -------
    HandSegmenter
    """

    return HandSegmenter(
        model_path=model_path,
        model_type=model_type,
    )