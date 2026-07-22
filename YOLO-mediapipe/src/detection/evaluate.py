"""
evaluate.py
===========

Evaluation utilities for the YOLO + MediaPipe Hand Tracking project.

This module provides functions for evaluating detection and tracking
performance, measuring runtime, and generating summary reports.

Author
------
Zahra Alipour
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# =============================================================================
# Evaluation Result
# =============================================================================


@dataclass
class EvaluationResult:
    """
    Stores evaluation metrics.
    """

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    fps: float
    total_frames: int
    detected_hands: int


# =============================================================================
# Evaluator
# =============================================================================


class Evaluator:
    """
    Evaluate the complete hand-tracking pipeline.
    """

    def __init__(self) -> None:

        self.start_time = None
        self.end_time = None

        self.frame_counter = 0
        self.hand_counter = 0

    # ---------------------------------------------------------------------

    def start_timer(self) -> None:
        """
        Start runtime measurement.
        """

        self.start_time = time.perf_counter()

    # ---------------------------------------------------------------------

    def stop_timer(self) -> None:
        """
        Stop runtime measurement.
        """

        self.end_time = time.perf_counter()

    # ---------------------------------------------------------------------

    def update(self, number_of_hands: int) -> None:
        """
        Update statistics after each processed frame.
        """

        self.frame_counter += 1
        self.hand_counter += number_of_hands

    # ---------------------------------------------------------------------

    def compute_fps(self) -> float:
        """
        Compute average FPS.
        """

        if self.start_time is None or self.end_time is None:
            return 0.0

        elapsed = self.end_time - self.start_time

        if elapsed <= 0:
            return 0.0

        return self.frame_counter / elapsed

    # ---------------------------------------------------------------------

    def classification_metrics(
        self,
        y_true: List[int],
        y_pred: List[int],
    ) -> EvaluationResult:
        """
        Compute classification metrics.
        """

        accuracy = accuracy_score(y_true, y_pred)

        precision = precision_score(
            y_true,
            y_pred,
            average="binary",
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            y_pred,
            average="binary",
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            y_pred,
            average="binary",
            zero_division=0,
        )

        fps = self.compute_fps()

        return EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            fps=fps,
            total_frames=self.frame_counter,
            detected_hands=self.hand_counter,
        )

    # ---------------------------------------------------------------------

    @staticmethod
    def print_report(
        y_true: List[int],
        y_pred: List[int],
    ) -> None:
        """
        Print classification report.
        """

        print("\nClassification Report")
        print("-" * 60)

        print(classification_report(y_true, y_pred))

    # ---------------------------------------------------------------------

    @staticmethod
    def print_confusion_matrix(
        y_true: List[int],
        y_pred: List[int],
    ) -> None:
        """
        Print confusion matrix.
        """

        cm = confusion_matrix(y_true, y_pred)

        print("\nConfusion Matrix")
        print("-" * 60)

        print(cm)

    # ---------------------------------------------------------------------

    @staticmethod
    def print_summary(
        result: EvaluationResult,
    ) -> None:
        """
        Print evaluation summary.
        """

        print("\nEvaluation Summary")
        print("=" * 60)

        print(f"Accuracy       : {result.accuracy:.4f}")
        print(f"Precision      : {result.precision:.4f}")
        print(f"Recall         : {result.recall:.4f}")
        print(f"F1-score       : {result.f1_score:.4f}")
        print(f"Average FPS    : {result.fps:.2f}")
        print(f"Frames         : {result.total_frames}")
        print(f"Detected Hands : {result.detected_hands}")

        print("=" * 60)