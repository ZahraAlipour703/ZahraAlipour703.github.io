"""
aruco_tracker.py
================

ArUco Marker Pose Estimation

This module detects ArUco markers attached to the fingers,
estimates their 6-DoF pose, computes rotation matrices,
Rodrigues vectors, quaternions and Euler angles.

The estimated poses are later used for
joint-angle computation.

Author
------
Zahra Alipour
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import cv2
import numpy as np
from scipy.spatial.transform import Rotation


# ----------------------------------------------------------
# Data Classes
# ----------------------------------------------------------

@dataclass
class MarkerPose:
    """
    Stores one marker pose.
    """

    marker_id: int

    rvec: np.ndarray

    tvec: np.ndarray

    rotation_matrix: np.ndarray

    quaternion: np.ndarray

    euler_angles: np.ndarray

    corners: np.ndarray


# ----------------------------------------------------------
# Main Tracker
# ----------------------------------------------------------

class ArucoTracker:

    """
    Detect and estimate ArUco marker poses.

    Pipeline

    Image
       ↓
    Detect Markers
       ↓
    Pose Estimation
       ↓
    Rodrigues
       ↓
    Rotation Matrix
       ↓
    Quaternion
       ↓
    Euler Angles
    """

    def __init__(

        self,

        camera_matrix: np.ndarray,

        distortion_coefficients: np.ndarray,

        marker_length: float,

        dictionary=cv2.aruco.DICT_6X6_250,

    ):

        self.camera_matrix = camera_matrix

        self.dist_coeffs = distortion_coefficients

        self.marker_length = marker_length

        self.dictionary = cv2.aruco.getPredefinedDictionary(
            dictionary
        )

        self.parameters = cv2.aruco.DetectorParameters()

        self.detector = cv2.aruco.ArucoDetector(
            self.dictionary,
            self.parameters,
        )

    # --------------------------------------------------

    def detect(

        self,

        image: np.ndarray,

    ) -> Dict[int, MarkerPose]:

        """
        Detect all markers in image.

        Returns
        -------
        dict

            key = marker id

            value = MarkerPose
        """

        corners, ids, _ = self.detector.detectMarkers(image)

        poses = {}

        if ids is None:

            return poses

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(

            corners,

            self.marker_length,

            self.camera_matrix,

            self.dist_coeffs,

        )

        for i, marker_id in enumerate(ids.flatten()):

            rvec = rvecs[i][0]

            tvec = tvecs[i][0]

            rotation_matrix, _ = cv2.Rodrigues(rvec)

            quaternion = Rotation.from_matrix(
                rotation_matrix
            ).as_quat()

            euler = Rotation.from_matrix(
                rotation_matrix
            ).as_euler(
                "xyz",
                degrees=True,
            )

            poses[int(marker_id)] = MarkerPose(

                marker_id=int(marker_id),

                rvec=rvec,

                tvec=tvec,

                rotation_matrix=rotation_matrix,

                quaternion=quaternion,

                euler_angles=euler,

                corners=corners[i],

            )

        return poses

    # --------------------------------------------------

    @staticmethod
    def average_quaternions(

        quaternions: List[np.ndarray],

    ) -> Optional[np.ndarray]:

        """
        Average multiple quaternions.

        Used when several faces of a cube
        are simultaneously visible.
        """

        if len(quaternions) == 0:

            return None

        matrix = np.zeros((4, 4))

        for q in quaternions:

            q = q.reshape(4, 1)

            matrix += q @ q.T

        matrix /= len(quaternions)

        eigenvalues, eigenvectors = np.linalg.eigh(matrix)

        quaternion = eigenvectors[:, -1]

        quaternion /= np.linalg.norm(quaternion)

        return quaternion

    # --------------------------------------------------

    @staticmethod
    def quaternion_to_matrix(

        quaternion: np.ndarray,

    ) -> np.ndarray:

        """
        Quaternion → Rotation Matrix
        """

        return Rotation.from_quat(
            quaternion
        ).as_matrix()

    # --------------------------------------------------

    @staticmethod
    def quaternion_to_euler(

        quaternion: np.ndarray,

    ) -> np.ndarray:

        """
        Quaternion → Euler Angles
        """

        return Rotation.from_quat(
            quaternion
        ).as_euler(
            "xyz",
            degrees=True,
        )

    # --------------------------------------------------

    def draw(

        self,

        image: np.ndarray,

        poses: Dict[int, MarkerPose],

    ) -> np.ndarray:

        """
        Draw marker borders,
        IDs and coordinate axes.
        """

        output = image.copy()

        for pose in poses.values():

            cv2.aruco.drawDetectedMarkers(

                output,

                [pose.corners],

                np.array([[pose.marker_id]]),

            )

            cv2.drawFrameAxes(

                output,

                self.camera_matrix,

                self.dist_coeffs,

                pose.rvec,

                pose.tvec,

                self.marker_length * 0.5,

            )

        return output