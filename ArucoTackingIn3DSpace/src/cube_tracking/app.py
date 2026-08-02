"""
Main application loop: capture -> detect -> track -> smooth -> draw -> display.

Purely local visualization — no data is transmitted anywhere.
"""

import time

import cv2
import numpy as np

from .config import (
    FRAME_HEIGHT,
    FRAME_WIDTH,
    VIDEO_DEVICE_INDEX,
    load_camera_calibration,
)
from .detection import MarkerDetector
from .geometry import average_quaternions
from .smoothing import CubeHistoryStore
from .visualization import draw_3d_cube, draw_fps, draw_info_panel, draw_vector_arrows

WINDOW_NAME = "Advanced Cube Tracking"


def process_frame(
    frame: np.ndarray,
    detector: MarkerDetector,
    histories: CubeHistoryStore,
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
    cm_to_pixel: float,
) -> np.ndarray:
    """
    Run detection, tracking, and drawing for a single frame.

    Returns:
        The frame with overlay blended in.
    """
    frame = cv2.undistort(frame, camera_matrix, distortion_coefficients)
    overlay = frame.copy()

    detected = detector.detect(frame, camera_matrix, distortion_coefficients, cm_to_pixel)

    for markers in detected.values():
        for m in markers:
            draw_vector_arrows(overlay, m['center_px'], m['quat'], length=30)

    for cube_idx, markers in detected.items():
        if not markers:
            continue

        avg_pos = np.mean([m['position'] for m in markers], axis=0)
        avg_quat = average_quaternions([m['quat'] for m in markers])
        faces = list({m['face'] for m in markers})

        sm_z = histories.smooth_z(cube_idx, avg_pos[2], avg_quat)
        final_pos = (avg_pos[0], avg_pos[1], sm_z * 100)

        history = histories[cube_idx]
        history['positions'].append(final_pos)
        history['orientations'].append(avg_quat)
        history['visible_faces'].update(faces)

        smooth_pos = np.mean(history['positions'], axis=0)
        smooth_quat = average_quaternions(history['orientations'])

        screen_center = (
            int(smooth_pos[0] / cm_to_pixel),
            int(smooth_pos[1] / cm_to_pixel),
        )
        is_avg = len(markers) > 2

        draw_3d_cube(overlay, screen_center, smooth_quat, faces, cube_idx, is_avg)
        draw_vector_arrows(overlay, screen_center, smooth_quat)
        draw_info_panel(overlay, cube_idx, smooth_pos, smooth_quat, faces, is_avg)

    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    return frame


def main() -> None:
    """Open the camera and run the live tracking/visualization loop."""
    calibration = load_camera_calibration()
    camera_matrix = calibration["camera_matrix"]
    distortion_coefficients = calibration["distortion_coefficients"]
    cm_to_pixel = calibration["cm_to_pixel"]

    detector = MarkerDetector()
    histories = CubeHistoryStore()

    capture = cv2.VideoCapture(VIDEO_DEVICE_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    prev_time = time.time()
    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                break

            current_time = time.time()
            fps = 1.0 / (current_time - prev_time)
            prev_time = current_time

            frame = process_frame(
                frame, detector, histories,
                camera_matrix, distortion_coefficients, cm_to_pixel,
            )
            draw_fps(frame, fps)
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('r'):
                histories.clear()
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
