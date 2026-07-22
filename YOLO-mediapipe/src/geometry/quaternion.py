"""
quaternion.py
=============

Quaternion mathematics utilities for the
YOLO + MediaPipe + ArUco Hand Tracking project.

This module provides:

- Rotation Matrix <-> Quaternion conversion
- Euler Angles <-> Quaternion conversion
- Quaternion multiplication
- Quaternion normalization
- Quaternion inverse
- Quaternion averaging
- Quaternion interpolation (SLERP)
- Vector rotation
- Quaternion distance

Author
------
Zahra Alipour
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


# =============================================================================
# Quaternion Dataclass
# =============================================================================


@dataclass
class Quaternion:
    """
    Quaternion representation.

    q = w + xi + yj + zk
    """

    w: float
    x: float
    y: float
    z: float

    # -------------------------------------------------------------------------

    def as_array(self) -> np.ndarray:
        """Return quaternion as numpy array."""

        return np.array(
            [self.w, self.x, self.y, self.z],
            dtype=np.float64,
        )

    # -------------------------------------------------------------------------

    def normalized(self) -> "Quaternion":
        """Return normalized quaternion."""

        q = self.as_array()

        norm = np.linalg.norm(q)

        if norm == 0:
            return Quaternion(1, 0, 0, 0)

        q /= norm

        return Quaternion(*q)

    # -------------------------------------------------------------------------

    def inverse(self) -> "Quaternion":
        """Quaternion inverse."""

        q = self.normalized()

        return Quaternion(
            q.w,
            -q.x,
            -q.y,
            -q.z,
        )

    # -------------------------------------------------------------------------

    def multiply(
        self,
        other: "Quaternion",
    ) -> "Quaternion":
        """Quaternion multiplication."""

        w1, x1, y1, z1 = self.as_array()
        w2, x2, y2, z2 = other.as_array()

        return Quaternion(
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2,
        )

    # -------------------------------------------------------------------------

    def rotation_matrix(self) -> np.ndarray:
        """Convert quaternion to rotation matrix."""

        q = self.normalized()

        w, x, y, z = q.as_array()

        return np.array([
            [
                1 - 2*(y**2 + z**2),
                2*(x*y - z*w),
                2*(x*z + y*w),
            ],
            [
                2*(x*y + z*w),
                1 - 2*(x**2 + z**2),
                2*(y*z - x*w),
            ],
            [
                2*(x*z - y*w),
                2*(y*z + x*w),
                1 - 2*(x**2 + y**2),
            ],
        ])

    # -------------------------------------------------------------------------

    def rotate_vector(
        self,
        vector: np.ndarray,
    ) -> np.ndarray:
        """
        Rotate a 3D vector.
        """

        return self.rotation_matrix() @ vector


# =============================================================================
# Rotation Matrix -> Quaternion
# =============================================================================


def from_rotation_matrix(
    R: np.ndarray,
) -> Quaternion:
    """
    Convert rotation matrix into quaternion.
    """

    trace = np.trace(R)

    if trace > 0:

        s = np.sqrt(trace + 1.0) * 2

        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s

    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:

        s = np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2

        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s

    elif R[1, 1] > R[2, 2]:

        s = np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2

        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s

    else:

        s = np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2

        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s

    return Quaternion(
        w,
        x,
        y,
        z,
    ).normalized()


# =============================================================================
# Euler Angles
# =============================================================================


def from_euler(
    roll: float,
    pitch: float,
    yaw: float,
) -> Quaternion:
    """
    Euler -> Quaternion.
    """

    cr = np.cos(roll / 2)
    sr = np.sin(roll / 2)

    cp = np.cos(pitch / 2)
    sp = np.sin(pitch / 2)

    cy = np.cos(yaw / 2)
    sy = np.sin(yaw / 2)

    return Quaternion(
        cr*cp*cy + sr*sp*sy,
        sr*cp*cy - cr*sp*sy,
        cr*sp*cy + sr*cp*sy,
        cr*cp*sy - sr*sp*cy,
    )


# =============================================================================
# Quaternion Distance
# =============================================================================


def angular_distance(
    q1: Quaternion,
    q2: Quaternion,
) -> float:
    """
    Angular distance in degrees.
    """

    dot = np.dot(
        q1.normalized().as_array(),
        q2.normalized().as_array(),
    )

    dot = np.clip(abs(dot), -1.0, 1.0)

    return np.degrees(
        2 * np.arccos(dot)
    )


# =============================================================================
# Quaternion Average
# =============================================================================


def average(
    quaternions: Iterable[Quaternion],
) -> Quaternion:
    """
    Average multiple quaternions.

    Used for averaging orientations from
    multiple ArUco markers.
    """

    quaternions = list(quaternions)

    if not quaternions:
        return Quaternion(1, 0, 0, 0)

    A = np.zeros((4, 4))

    for q in quaternions:

        v = q.normalized().as_array()

        A += np.outer(v, v)

    eigenvalues, eigenvectors = np.linalg.eigh(A)

    q = eigenvectors[:, np.argmax(eigenvalues)]

    return Quaternion(*q).normalized()


# =============================================================================
# SLERP
# =============================================================================


def slerp(
    q1: Quaternion,
    q2: Quaternion,
    t: float,
) -> Quaternion:
    """
    Spherical Linear Interpolation.
    """

    q1 = q1.normalized()
    q2 = q2.normalized()

    dot = np.dot(
        q1.as_array(),
        q2.as_array(),
    )

    if dot < 0:
        q2 = Quaternion(
            -q2.w,
            -q2.x,
            -q2.y,
            -q2.z,
        )
        dot = -dot

    if dot > 0.9995:

        result = (
            q1.as_array()
            + t * (q2.as_array() - q1.as_array())
        )

        result /= np.linalg.norm(result)

        return Quaternion(*result)

    theta0 = np.arccos(dot)

    theta = theta0 * t

    sin_theta = np.sin(theta)

    sin_theta0 = np.sin(theta0)

    s1 = np.cos(theta) - dot * sin_theta / sin_theta0
    s2 = sin_theta / sin_theta0

    result = (
        s1 * q1.as_array()
        + s2 * q2.as_array()
    )

    return Quaternion(*result).normalized()