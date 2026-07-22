"""
main.py
=======

Main entry point for the YOLO + MediaPipe Hand Tracking project.

Pipeline
--------
Video
    ↓
YOLO Detection          (src.detection.detector.YOLODetector)
    ↓
MediaPipe Hand Landmarks (src.tracking.mediapipe_tracker.MediaPipeTracker)
    ↓
Joint Angle Calculation   (src.geometry.angle_calculator.AngleCalculator)
    ↓
Visualization             (src.visualization.visualization.Visualizer)
    ↓
Output Video + CSV

ArUco marker pose / quaternion estimation is available (src.tracking.aruco_tracker,
src.geometry.coordinate_system) but is not wired in by default here, since it
requires a real camera calibration (camera_matrix + distortion_coefficients) that
this project does not yet provide. Pass your own calibration values to enable it
-- see the `aruco` section below.

Author
------
Zahra Alipour
"""

from __future__ import annotations

import argparse
import time
from dataclasses import asdict
from pathlib import Path

import cv2

from src.detection.detector import YOLODetector
from src.geometry.angle_calculator import AngleCalculator
from src.preprocessing.preprocessing import VideoReader, VideoWriter
from src.tracking.mediapipe_tracker import MediaPipeTracker
from src.tracking.tracker import HandTracker
from src.utils.config import cfg
from src.utils.logger import get_logger
from src.visualization.visualization import Visualizer

logger = get_logger("Main")


# =============================================================================
# Argument Parser
# =============================================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="YOLO + MediaPipe Hand Tracking"
    )

    parser.add_argument(
        "--source",
        type=str,
        default=cfg.input_path,
        help="Video path or camera index",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output video",
    )

    return parser.parse_args()


# =============================================================================
# Main
# =============================================================================

def main():

    args = parse_args()

    logger.info("Initializing modules...")

    detector = YOLODetector(
        model_path=cfg.yolo_model,
        confidence=cfg.confidence,
        device=cfg.device,
    )

    mediapipe_tracker = MediaPipeTracker(
        max_num_hands=cfg.max_hands,
        detection_confidence=cfg.detection_confidence,
        tracking_confidence=cfg.tracking_confidence,
    )

    angle_calculator = AngleCalculator()

    hand_tracker = HandTracker(
        detector=detector,
        landmark_tracker=mediapipe_tracker,
        angle_calculator=angle_calculator,
    )

    visualizer = Visualizer()

    # Camera index vs. video file path.
    source = int(args.source) if str(args.source).isdigit() else args.source

    reader = VideoReader(source)
    writer = None

    try:
        for frame in reader.frames():

            # -----------------------------------------------------
            # Full pipeline for one frame: YOLO -> MediaPipe -> angles
            # -----------------------------------------------------

            result = hand_tracker.process(frame)

            angles_dict = result.angles  # already a flat {name: value} dict, or None

            # -----------------------------------------------------
            # Visualization
            # -----------------------------------------------------

            output = visualizer.draw_pipeline(
                frame=result.frame,
                detections=result.detections if cfg.draw_bbox else [],
                hands=result.hands if cfg.draw_landmarks else [],
                poses=[],           # ArUco not wired in -- see module docstring
                angles=angles_dict if cfg.draw_angles else None,
                fps=result.fps,
                camera_matrix=None,
                distortion=None,
            )

            # -----------------------------------------------------
            # Video Writer
            # -----------------------------------------------------

            if args.save:

                if writer is None:

                    h, w = output.shape[:2]

                    out_path = str(Path(cfg.video_output) / "output.mp4")

                    writer = VideoWriter(
                        output_path=out_path,
                        fps=30,
                        frame_size=(w, h),
                    )

                writer.write(output)

            # -----------------------------------------------------
            # Display
            # -----------------------------------------------------

            cv2.imshow(
                "YOLO + MediaPipe Hand Tracking",
                output,
            )

            key = cv2.waitKey(1)

            if key == ord("q"):
                break

    finally:

        logger.info("Finished.")

        reader.release()
        mediapipe_tracker.close()
        cv2.destroyAllWindows()

        if writer is not None:
            writer.release()


# =============================================================================

if __name__ == "__main__":

    main()
