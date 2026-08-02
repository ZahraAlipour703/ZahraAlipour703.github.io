"""
ArUco marker detection and per-marker pose estimation.

Isolates all direct cv2.aruco usage so tracking/visualization code does not
need to know which fiducial system is in use.
"""

from collections import defaultdict

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

from .config import FACE_ROTATION_CORRECTIONS, MARKER_SIZE_M, NUM_CUBES
from .geometry import get_cube_and_face


class MarkerDetector:
    """Wraps cv2.aruco detection + pose estimation for a fixed marker size."""

    def __init__(self, dictionary_id: int = cv2.aruco.DICT_6X6_250):
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self.params = cv2.aruco.DetectorParameters()

    def detect(
        self,
        frame: np.ndarray,
        camera_matrix: np.ndarray,
        distortion_coefficients: np.ndarray,
        cm_to_pixel: float,
    ) -> dict:
        """
        Detect markers in a frame and group per-marker pose data by cube index.

        Args:
            frame: Undistorted BGR frame.
            camera_matrix: Camera intrinsics matrix.
            distortion_coefficients: Camera distortion coefficients.
            cm_to_pixel: Pixel-to-centimeter conversion factor.

        Returns:
            Dict mapping cube_index -> list of per-marker detections, each a
            dict with 'center_px', 'position' (x_cm, y_cm, raw_z), 'quat', 'face'.
        """
        corners, ids, _ = cv2.aruco.detectMarkers(
            frame, self.dictionary, parameters=self.params
        )
        detected = defaultdict(list)

        if ids is None:
            return detected

        for corner, marker_id in zip(corners, ids.flatten()):
            cube_idx, face_lbl = get_cube_and_face(int(marker_id))
            if cube_idx >= NUM_CUBES:
                continue

            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corner, MARKER_SIZE_M, camera_matrix, distortion_coefficients
            )
            center_px = tuple(map(int, corner[0].mean(axis=0)))
            x_cm = center_px[0] * cm_to_pixel
            y_cm = center_px[1] * cm_to_pixel
            raw_z = tvecs[0][0][2]

            rot_marker = R.from_rotvec(rvecs[0][0]).as_matrix()
            corrected_mat = FACE_ROTATION_CORRECTIONS[face_lbl].as_matrix() @ rot_marker
            quat = R.from_matrix(corrected_mat).as_quat()

            detected[cube_idx].append({
                'center_px': center_px,
                'position': (x_cm, y_cm, raw_z),
                'quat': quat,
                'face': face_lbl,
            })

        return detected
