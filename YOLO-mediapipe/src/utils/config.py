"""
config.py
=========

Central configuration manager for the YOLO + MediaPipe Hand Tracking project.

Features
--------
- Loads configuration from config.yaml
- Validates required sections
- Resolves project paths automatically
- Creates output directories if they do not exist
- Supports nested configuration access
- Provides type-safe helper properties

Author
------
Zahra Alipour
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


# ==============================================================================
# Project Paths
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_CONFIG = PROJECT_ROOT / "config.yaml"


# ==============================================================================
# Configuration Manager
# ==============================================================================


class Config:
    """
    Configuration manager.

    Examples
    --------
    >>> cfg = Config()
    >>> print(cfg.yolo_model)
    >>> print(cfg.confidence)
    >>> print(cfg.output_path)
    """

    REQUIRED_SECTIONS = (
        "paths",
        "yolo",
        "mediapipe",
        "tracking",
        "visualization",
        "output",
    )

    # -------------------------------------------------------------------------

    def __init__(self, config_file: str | Path | None = None) -> None:

        self.config_file = Path(config_file) if config_file else DEFAULT_CONFIG

        if not self.config_file.exists():
            raise FileNotFoundError(
                f"\nConfiguration file not found:\n{self.config_file}"
            )

        self.config = self._load_yaml()

        self._validate()

        self._create_directories()

    # -------------------------------------------------------------------------

    def _load_yaml(self) -> dict:
        """
        Load YAML configuration file.
        """

        try:

            with open(
                self.config_file,
                "r",
                encoding="utf-8",
            ) as file:

                return yaml.safe_load(file)

        except yaml.YAMLError as error:

            raise RuntimeError(
                f"Invalid YAML configuration.\n{error}"
            ) from error

    # -------------------------------------------------------------------------

    def _validate(self) -> None:
        """
        Validate required configuration sections.
        """

        for section in self.REQUIRED_SECTIONS:

            if section not in self.config:

                raise ValueError(
                    f"Missing section '{section}' in config.yaml"
                )

    # -------------------------------------------------------------------------

    def _create_directories(self) -> None:
        """
        Automatically create required output folders.
        """

        folders = [

            self.output_path,

            self.csv_path,

            self.image_output,

            self.video_output,

            self.log_output,

        ]

        for folder in folders:

            Path(folder).mkdir(
                parents=True,
                exist_ok=True,
            )

    # -------------------------------------------------------------------------

    def get(
        self,
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve nested configuration values.

        Example
        -------
        cfg.get("yolo", "confidence")
        """

        value = self.config

        for key in keys:

            if not isinstance(value, dict):
                return default

            value = value.get(key, default)

        return value

    # ==========================================================================
    # PATHS
    # ==========================================================================

    @property
    def model_path(self) -> str:
        return str(PROJECT_ROOT / self.get("paths", "model"))

    @property
    def input_path(self) -> str:
        return str(PROJECT_ROOT / self.get("paths", "input"))

    @property
    def output_path(self) -> str:
        return str(PROJECT_ROOT / self.get("paths", "output"))

    @property
    def csv_path(self) -> str:
        return str(PROJECT_ROOT / self.get("paths", "csv"))

    @property
    def image_output(self) -> str:
        return str(PROJECT_ROOT / "outputs/images")

    @property
    def video_output(self) -> str:
        return str(PROJECT_ROOT / "outputs/videos")

    @property
    def log_output(self) -> str:
        return str(PROJECT_ROOT / "outputs/logs")

    # ==========================================================================
    # YOLO
    # ==========================================================================

    @property
    def yolo_model(self) -> str:
        return str(PROJECT_ROOT / self.get("yolo", "model"))

    @property
    def confidence(self) -> float:
        return float(self.get("yolo", "confidence"))

    @property
    def iou(self) -> float:
        return float(self.get("yolo", "iou"))

    @property
    def device(self) -> str:
        return str(self.get("yolo", "device"))

    # ==========================================================================
    # MEDIAPIPE
    # ==========================================================================

    @property
    def max_hands(self) -> int:
        return int(self.get("mediapipe", "max_hands"))

    @property
    def detection_confidence(self) -> float:
        return float(self.get("mediapipe", "detection_confidence"))

    @property
    def tracking_confidence(self) -> float:
        return float(self.get("mediapipe", "tracking_confidence"))

    # ==========================================================================
    # TRACKING
    # ==========================================================================

    @property
    def tracker(self) -> str:
        return str(self.get("tracking", "tracker"))

    @property
    def max_age(self) -> int:
        return int(self.get("tracking", "max_age"))

    @property
    def min_hits(self) -> int:
        return int(self.get("tracking", "min_hits"))

    # ==========================================================================
    # VISUALIZATION
    # ==========================================================================

    @property
    def draw_bbox(self) -> bool:
        return bool(self.get("visualization", "draw_bbox"))

    @property
    def draw_landmarks(self) -> bool:
        return bool(self.get("visualization", "draw_landmarks"))

    @property
    def draw_angles(self) -> bool:
        return bool(self.get("visualization", "draw_angles"))

    @property
    def show_fps(self) -> bool:
        return bool(self.get("visualization", "show_fps"))

    # ==========================================================================
    # OUTPUT
    # ==========================================================================

    @property
    def save_video(self) -> bool:
        return bool(self.get("output", "save_video"))

    @property
    def save_csv(self) -> bool:
        return bool(self.get("output", "save_csv"))

    @property
    def save_images(self) -> bool:
        return bool(self.get("output", "save_images"))

    # -------------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            "Config("
            f"model='{self.yolo_model}', "
            f"confidence={self.confidence}, "
            f"device='{self.device}'"
            ")"
        )


# ==============================================================================
# Singleton
# ==============================================================================
# Every other module imports this instance directly:
#     from src.utils.config import cfg
cfg = Config()