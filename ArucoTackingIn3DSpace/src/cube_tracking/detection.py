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
        # OpenCV >= 4.7 moved detection to the ArucoDetector class; older
        # versions only have the free-function cv2.aruco.detectMarkers.
        self._detector = None
        if hasattr(cv2.aruco, "ArucoDetector"):
            self._detector = cv2.aruco.ArucoDetector(self.dictionary, self.params)

    def _detect_markers(self, frame: np.ndarray):
        if self._detector is not None:
            return self._detector.detectMarkers(frame)
        return cv2.aruco.detectMarkers(frame, self.dictionary, parameters=self.params)

    def _estimate_pose(
        self,
        corner: np.ndarray,
        camera_matrix: np.ndarray,
        distortion_coefficients: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Estimate a single marker's pose via solvePnP.

        Replaces cv2.aruco.estimatePoseSingleMarkers, which was removed in
        OpenCV 5.0 — solvePnP works identically across all OpenCV versions.

        Returns:
            Tuple of (rvec, tvec), each shape (3,).
        """
        half = MARKER_SIZE_M / 2.0
        object_points = np.array([
            [-half, half, 0],
            [half, half, 0],
            [half, -half, 0],
            [-half, -half, 0],
        ], dtype=np.float32)

        ok, rvec, tvec = cv2.solvePnP(
            object_points, corner[0], camera_matrix, distortion_coefficients
        )
        if not ok:
            raise RuntimeError("solvePnP failed to estimate marker pose")
        return rvec.flatten(), tvec.flatten()

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
        corners, ids, _ = self._detect_markers(frame)
        detected = defaultdict(list)

        if ids is None:
            return detected

        for corner, marker_id in zip(corners, ids.flatten()):
            cube_idx, face_lbl = get_cube_and_face(int(marker_id))
            if cube_idx >= NUM_CUBES:
                continue

            rvec, tvec = self._estimate_pose(corner, camera_matrix, distortion_coefficients)
            center_px = tuple(map(int, corner[0].mean(axis=0)))
            x_cm = center_px[0] * cm_to_pixel
            y_cm = center_px[1] * cm_to_pixel
            raw_z = tvec[2]

            rot_marker = R.from_rotvec(rvec).as_matrix()
            corrected_mat = FACE_ROTATION_CORRECTIONS[face_lbl].as_matrix() @ rot_marker
            quat = R.from_matrix(corrected_mat).as_quat()

            detected[cube_idx].append({
                'center_px': center_px,
                'position': (x_cm, y_cm, raw_z),
                'quat': quat,
                'face': face_lbl,
            })

        return detected
