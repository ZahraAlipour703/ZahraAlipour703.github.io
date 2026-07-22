"""
train.py
========

YOLOv8 training module.

This module trains a custom YOLOv8 model on the prepared
hand dataset.

Dataset Structure
-----------------
dataset/
│
├── images/
│   ├── train/
│   ├── val/
│   └── test/
│
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
│
└── dataset.yaml

Author
------
Zahra Alipour
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ultralytics import YOLO


class YOLOTrainer:
    """
    Wrapper around the Ultralytics YOLO trainer.

    Example
    -------
    >>> trainer = YOLOTrainer("yolov8n.pt")
    >>> trainer.train("dataset.yaml")
    """

    def __init__(self, model_path: str = "models/yolov8n.pt") -> None:
        """
        Parameters
        ----------
        model_path
            Path to pretrained YOLO weights.
        """

        self.model_path = model_path
        self.model = YOLO(model_path)

    # ------------------------------------------------------------------

    def train(
        self,
        data: str,
        epochs: int = 100,
        imgsz: int = 640,
        batch: int = 16,
        device: str = "0",
        project: str = "runs/train",
        name: str = "hand_detector",
        workers: int = 8,
        patience: int = 50,
        optimizer: str = "AdamW",
        lr0: float = 0.001,
        weight_decay: float = 0.0005,
        save: bool = True,
        verbose: bool = True,
    ):
        """
        Train YOLO model.
        """

        results = self.model.train(
            data=data,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            project=project,
            name=name,
            workers=workers,
            patience=patience,
            optimizer=optimizer,
            lr0=lr0,
            weight_decay=weight_decay,
            save=save,
            verbose=verbose,
        )

        return results

    # ------------------------------------------------------------------

    def resume(self, checkpoint: str):
        """
        Resume training from checkpoint.
        """

        self.model = YOLO(checkpoint)

        return self.model.train(resume=True)

    # ------------------------------------------------------------------

    def validate(self):
        """
        Evaluate trained model.
        """

        return self.model.val()

    # ------------------------------------------------------------------

    def export(
        self,
        format: str = "onnx",
        imgsz: int = 640,
    ):
        """
        Export trained model.

        Supported formats
        -----------------
        onnx
        openvino
        engine
        torchscript
        tflite
        """

        return self.model.export(
            format=format,
            imgsz=imgsz,
        )


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    """
    Example training entry point.
    """

    dataset = Path("data/dataset.yaml")

    if not dataset.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found:\n{dataset}"
        )

    trainer = YOLOTrainer(
        model_path="models/yolov8n.pt"
    )

    trainer.train(
        data=str(dataset),
        epochs=100,
        imgsz=640,
        batch=16,
        device="0",
    )


if __name__ == "__main__":
    main()