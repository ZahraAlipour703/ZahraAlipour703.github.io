"""
Pure geometry/math helpers for cube tracking.

No OpenCV drawing or camera I/O lives here — everything in this module is
unit-testable in isolation.
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

from .config import ANGLE_THRESHOLD_DEG, FACE_NAMES, MARKERS_PER_CUBE


def get_cube_and_face(marker_id: int) -> tuple[int, str]:
    """
    Map a marker ID to its cube index and face name.

    Args:
        marker_id: Identifier of detected ArUco marker.

    Returns:
        Tuple containing cube index and face label.
    """
    cube_idx = marker_id // MARKERS_PER_CUBE
    face_idx = marker_id % MARKERS_PER_CUBE
    return cube_idx, FACE_NAMES[face_idx]


def average_quaternions(quats: list[np.ndarray]) -> np.ndarray:
    """
    Compute the average quaternion using eigen decomposition.

    Args:
        quats: List of quaternions as numpy arrays.

    Returns:
        Averaged quaternion as numpy array.
    """
    q_array = np.stack(quats)
    covariance = q_array.T @ q_array
    _, eigenvecs = np.linalg.eigh(covariance)
    return eigenvecs[:, -1]


def is_quaternion_perpendicular(quat: np.ndarray) -> bool:
    """
    Determine if rotation represented by quaternion is near-perpendicular.

    Args:
        quat: Quaternion as numpy array [x, y, z, w].

    Returns:
        True if tilt angle ~90°, False otherwise.
    """
    try:
        rot = R.from_quat(quat)
        zyx = rot.as_euler('zyx', degrees=True)
        return abs(abs(zyx[0]) - 90) < ANGLE_THRESHOLD_DEG
    except Exception:
        return False
