#!/usr/bin/env python3
"""
Camera calibration tool.

Captures checkerboard images from the webcam, computes the camera intrinsics
and distortion coefficients, and writes them to config/camera_calibration.yaml
in the format expected by cube_tracking.config.load_camera_calibration.

Usage:
    python tools/calibrate_camera.py --rows 6 --cols 9 --square-size-cm 2.5
"""

import argparse
from pathlib import Path

import cv2
import numpy as np
import yaml

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "config" / "camera_calibration.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate a camera using a checkerboard pattern.")
    parser.add_argument("--rows", type=int, default=6, help="Inner corner rows of the checkerboard.")
    parser.add_argument("--cols", type=int, default=9, help="Inner corner columns of the checkerboard.")
    parser.add_argument("--square-size-cm", type=float, required=True,
                         help="Physical size of one checkerboard square, in cm.")
    parser.add_argument("--device", type=int, default=0, help="Camera device index.")
    parser.add_argument("--num-captures", type=int, default=15,
                         help="Number of valid checkerboard detections to collect.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                         help="Output path for camera_calibration.yaml.")
    return parser.parse_args()


def run_calibration(args: argparse.Namespace) -> None:
    pattern_size = (args.cols, args.rows)
    objp = np.zeros((args.rows * args.cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2) * args.square_size_cm

    obj_points, img_points = [], []
    capture = cv2.VideoCapture(args.device)

    print("Press SPACE to capture a frame when the checkerboard is detected, 'q' to finish early.")
    while len(obj_points) < args.num_captures:
        ret, frame = capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, pattern_size)

        display = frame.copy()
        if found:
            cv2.drawChessboardCorners(display, pattern_size, corners, found)
        cv2.putText(display, f"Captured: {len(obj_points)}/{args.num_captures}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Calibration", display)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord(' ') and found:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            obj_points.append(objp)
            img_points.append(refined)
            print(f"Captured {len(obj_points)}/{args.num_captures}")

    capture.release()
    cv2.destroyAllWindows()

    if len(obj_points) < 5:
        raise RuntimeError("Not enough valid captures to calibrate (need at least 5).")

    ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
        obj_points, img_points, gray.shape[::-1], None, None
    )
    print(f"Calibration RMS reprojection error: {ret:.4f}")

    print("Measure the pixel width of a known real-world distance in a live frame")
    print("to compute cm_to_pixel, then update the output file's value if needed.")

    output = {
        "camera_matrix": camera_matrix.tolist(),
        "distortion_coefficients": dist_coeffs.reshape(-1, 1).tolist(),
        "cm_to_pixel": None,  # fill in after measuring a known reference distance
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        yaml.safe_dump(output, f, sort_keys=False)

    print(f"Wrote calibration to {args.output}")


if __name__ == "__main__":
    run_calibration(parse_args())
