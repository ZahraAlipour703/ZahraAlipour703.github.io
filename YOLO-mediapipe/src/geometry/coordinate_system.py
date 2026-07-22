"""
coordinate_system.py
====================

Coordinate system utilities for ArUco-based hand tracking.

This module provides functions for converting OpenCV pose
estimations into homogeneous transformation matrices and
performing coordinate transformations.

Coordinate Frames
-----------------
Camera Frame
        ↓
ArUco Marker Frame
        ↓
Finger Local Frame
        ↓
Hand Frame

Author
------
Zahra Alipour
"""

from __future__ import annotations

import cv2
import numpy as np


class CoordinateSystem:
    """
    Coordinate system utilities.

    Responsible for:

    • Rotation matrix generation
    • Homogeneous transformations
    • Coordinate conversions
    • Pose inversion
    """

    # -------------------------------------------------------------

    @staticmethod
    def rvec_to_rotation(rvec: np.ndarray) -> np.ndarray:
        """
        Convert Rodrigues vector to rotation matrix.
        """

        rotation_matrix, _ = cv2.Rodrigues(rvec)

        return rotation_matrix

    # -------------------------------------------------------------

    @staticmethod
    def rotation_to_rvec(rotation: np.ndarray) -> np.ndarray:
        """
        Convert rotation matrix to Rodrigues vector.
        """

        rvec, _ = cv2.Rodrigues(rotation)

        return rvec

    # -------------------------------------------------------------

    @staticmethod
    def transformation_matrix(
        rotation: np.ndarray,
        translation: np.ndarray,
    ) -> np.ndarray:
        """
        Create a 4×4 homogeneous transformation matrix.

        T =
        | R t |
        | 0 1 |
        """

        transform = np.eye(4, dtype=np.float64)

        transform[:3, :3] = rotation
        transform[:3, 3] = translation.reshape(3)

        return transform

    # -------------------------------------------------------------

    @staticmethod
    def pose_to_matrix(
        rvec: np.ndarray,
        tvec: np.ndarray,
    ) -> np.ndarray:
        """
        Convert OpenCV pose to transformation matrix.
        """

        rotation = CoordinateSystem.rvec_to_rotation(rvec)

        return CoordinateSystem.transformation_matrix(
            rotation,
            tvec,
        )

    # -------------------------------------------------------------

    @staticmethod
    def invert(matrix: np.ndarray) -> np.ndarray:
        """
        Invert a homogeneous transformation.
        """

        rotation = matrix[:3, :3]
        translation = matrix[:3, 3]

        inv = np.eye(4)

        inv[:3, :3] = rotation.T
        inv[:3, 3] = -rotation.T @ translation

        return inv

    # -------------------------------------------------------------

    @staticmethod
    def transform_point(
        point: np.ndarray,
        transform: np.ndarray,
    ) -> np.ndarray:
        """
        Transform a 3D point using a homogeneous matrix.
        """

        point_h = np.append(point, 1.0)

        transformed = transform @ point_h

        return transformed[:3]

    # -------------------------------------------------------------

    @staticmethod
    def transform_points(
        points: np.ndarray,
        transform: np.ndarray,
    ) -> np.ndarray:
        """
        Transform multiple 3D points.

        Parameters
        ----------
        points : (N,3)

        Returns
        -------
        (N,3)
        """

        transformed = []

        for point in points:

            transformed.append(
                CoordinateSystem.transform_point(
                    point,
                    transform,
                )
            )

        return np.asarray(transformed)

    # -------------------------------------------------------------

    @staticmethod
    def relative_transform(
        parent: np.ndarray,
        child: np.ndarray,
    ) -> np.ndarray:
        """
        Compute child pose relative to parent.

        T_relative = T_parent^-1 * T_child
        """

        return CoordinateSystem.invert(parent) @ child

    # -------------------------------------------------------------

    @staticmethod
    def compose(
        first: np.ndarray,
        second: np.ndarray,
    ) -> np.ndarray:
        """
        Compose two transformations.
        """

        return first @ second

    # -------------------------------------------------------------

    @staticmethod
    def rotation_only(matrix: np.ndarray) -> np.ndarray:
        """
        Extract rotation matrix.
        """

        return matrix[:3, :3]

    # -------------------------------------------------------------

    @staticmethod
    def translation_only(matrix: np.ndarray) -> np.ndarray:
        """
        Extract translation vector.
        """

        return matrix[:3, 3]

    # -------------------------------------------------------------

    @staticmethod
    def camera_axes(length: float = 0.05) -> np.ndarray:
        """
        Generate XYZ axes for visualization.

        Returns
        -------
        ndarray (4,3)
        """

        return np.array(
            [
                [0.0, 0.0, 0.0],
                [length, 0.0, 0.0],
                [0.0, length, 0.0],
                [0.0, 0.0, length],
            ],
            dtype=np.float32,
        )

    # -------------------------------------------------------------

    @staticmethod
    def project_axes(
        rvec: np.ndarray,
        tvec: np.ndarray,
        camera_matrix: np.ndarray,
        distortion: np.ndarray,
        axis_length: float = 0.05,
    ) -> np.ndarray:
        """
        Project XYZ coordinate axes into the image.
        """

        axes = CoordinateSystem.camera_axes(axis_length)

        image_points, _ = cv2.projectPoints(
            axes,
            rvec,
            tvec,
            camera_matrix,
            distortion,
        )

        return image_points.reshape(-1, 2)

    # -------------------------------------------------------------

    @staticmethod
    def is_valid_rotation(rotation: np.ndarray) -> bool:
        """
        Validate a rotation matrix.
        """

        should_be_identity = rotation.T @ rotation

        identity = np.eye(3)

        error = np.linalg.norm(identity - should_be_identity)

        determinant = np.linalg.det(rotation)

        return error < 1e-6 and abs(determinant - 1.0) < 1e-6