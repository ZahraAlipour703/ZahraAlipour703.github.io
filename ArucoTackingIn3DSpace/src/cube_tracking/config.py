"""
Central configuration for the cube tracking pipeline.

Camera-specific values (intrinsics, distortion, pixel-to-cm ratio) are loaded
from config/camera_calibration.yaml rather than hardcoded here, since they
depend on the physical camera/rig in use. See tools/calibrate_camera.py.
"""

from pathlib import Path

import numpy as np
import yaml
from scipy.spatial.transform import Rotation as R

# ---------------------------------------------------------------------------- #
#                              CAMERA / CAPTURE                                #
# ---------------------------------------------------------------------------- #
VIDEO_DEVICE_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

DEFAULT_CALIBRATION_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "camera_calibration.yaml"
)


def load_camera_calibration(path: Path = DEFAULT_CALIBRATION_PATH) -> dict:
    """
    Load camera intrinsics/distortion and the pixel-to-cm ratio from YAML.

    Args:
        path: Path to a camera_calibration.yaml file.

    Returns:
        Dict with keys 'camera_matrix', 'distortion_coefficients', 'cm_to_pixel'.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return {
        "camera_matrix": np.array(data["camera_matrix"]),
        "distortion_coefficients": np.array(data["distortion_coefficients"]),
        "cm_to_pixel": float(data["cm_to_pixel"]),
    }


# ---------------------------------------------------------------------------- #
#                              CUBE / MARKER LAYOUT                            #
# ---------------------------------------------------------------------------- #
NUM_CUBES = 6              # depends on the use case
MARKERS_PER_CUBE = 6
MARKER_SIZE_M = 0.01       # marker side length in meters
BASE_CUBE_PIXEL_SIZE = 30
HISTORY_LENGTH = 15

FACE_NAMES = ['Top', 'Front', 'Back', 'Right', 'Left', 'Bottom']

# Rotation corrections for each face: z->top, y->right, x->forward
FACE_ROTATION_CORRECTIONS = {
    'Top': R.identity(),
    'Front': R.from_euler('x', 90, degrees=True),
    'Back': R.from_euler('x', 90, degrees=True) * R.from_euler('y', 180, degrees=True),
    'Right': R.from_euler('y', 90, degrees=True),
    'Left': R.from_euler('y', -90, degrees=True),
    'Bottom': R.from_euler('x', 180, degrees=True),
}

# ---------------------------------------------------------------------------- #
#                              SMOOTHING                                       #
# ---------------------------------------------------------------------------- #
BASE_SMOOTHING = 0.2
PERPENDICULAR_SMOOTHING = 0.1
MAX_Z_DELTA = 0.1
ANGLE_THRESHOLD_DEG = 5

# ---------------------------------------------------------------------------- #
#                              VISUALIZATION                                   #
# ---------------------------------------------------------------------------- #
CUBE_COLORS = [
    (0, 255, 0), (0, 0, 255), (255, 0, 0),
    (255, 255, 0), (0, 255, 255), (255, 0, 255),
]
VECTOR_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
EDGE_PAIRS = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
