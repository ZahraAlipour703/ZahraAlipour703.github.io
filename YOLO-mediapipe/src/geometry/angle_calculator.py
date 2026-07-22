"""
angle_calculator.py
===================

Joint Angle Computation Module

Computes hand joint angles from

1. MediaPipe landmarks
2. ArUco marker orientations
3. Quaternion rotations

Outputs

- Wrist Flexion / Extension
- MCP Angles
- PIP Angles
- DIP Angles
- Thumb Angles

Author
------
Zahra Alipour
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from scipy.spatial.transform import Rotation


# ---------------------------------------------------------
# Dataclass
# ---------------------------------------------------------

@dataclass
class JointAngles:

    wrist: float

    thumb_mcp: float
    thumb_ip: float

    index_mcp: float
    index_pip: float
    index_dip: float

    middle_mcp: float
    middle_pip: float
    middle_dip: float

    ring_mcp: float
    ring_pip: float
    ring_dip: float

    pinky_mcp: float
    pinky_pip: float
    pinky_dip: float


# ---------------------------------------------------------
# Angle Calculator
# ---------------------------------------------------------

class AngleCalculator:

    """
    Computes joint angles.

    Can operate on

    • MediaPipe landmarks

    • ArUco rotations

    • Quaternion poses
    """

    # -----------------------------------------------------

    @staticmethod
    def vector(a, b):

        return np.array(b) - np.array(a)

    # -----------------------------------------------------

    @staticmethod
    def normalize(v):

        norm = np.linalg.norm(v)

        if norm == 0:

            return v

        return v / norm

    # -----------------------------------------------------

    @staticmethod
    def angle_between(v1, v2):

        """
        Returns angle in degrees.
        """

        v1 = AngleCalculator.normalize(v1)

        v2 = AngleCalculator.normalize(v2)

        cosine = np.clip(

            np.dot(v1, v2),

            -1.0,

            1.0,

        )

        return np.degrees(np.arccos(cosine))

    # -----------------------------------------------------

    @staticmethod
    def joint_angle(

        p1,

        p2,

        p3,

    ):

        """
        Angle formed by

        p1 ---- p2 ---- p3
        """

        v1 = AngleCalculator.vector(

            p2,

            p1,

        )

        v2 = AngleCalculator.vector(

            p2,

            p3,

        )

        return AngleCalculator.angle_between(

            v1,

            v2,

        )

    # -----------------------------------------------------

    def compute_from_landmarks(

        self,

        landmarks: List[tuple],

    ) -> JointAngles:

        """
        Compute all hand angles from

        MediaPipe landmarks.
        """

        wrist = self.joint_angle(

            landmarks[0],

            landmarks[5],

            landmarks[9],

        )

        thumb_mcp = self.joint_angle(

            landmarks[1],

            landmarks[2],

            landmarks[3],

        )

        thumb_ip = self.joint_angle(

            landmarks[2],

            landmarks[3],

            landmarks[4],

        )

        index_mcp = self.joint_angle(

            landmarks[0],

            landmarks[5],

            landmarks[6],

        )

        index_pip = self.joint_angle(

            landmarks[5],

            landmarks[6],

            landmarks[7],

        )

        index_dip = self.joint_angle(

            landmarks[6],

            landmarks[7],

            landmarks[8],

        )

        middle_mcp = self.joint_angle(

            landmarks[0],

            landmarks[9],

            landmarks[10],

        )

        middle_pip = self.joint_angle(

            landmarks[9],

            landmarks[10],

            landmarks[11],

        )

        middle_dip = self.joint_angle(

            landmarks[10],

            landmarks[11],

            landmarks[12],

        )

        ring_mcp = self.joint_angle(

            landmarks[0],

            landmarks[13],

            landmarks[14],

        )

        ring_pip = self.joint_angle(

            landmarks[13],

            landmarks[14],

            landmarks[15],

        )

        ring_dip = self.joint_angle(

            landmarks[14],

            landmarks[15],

            landmarks[16],

        )

        pinky_mcp = self.joint_angle(

            landmarks[0],

            landmarks[17],

            landmarks[18],

        )

        pinky_pip = self.joint_angle(

            landmarks[17],

            landmarks[18],

            landmarks[19],

        )

        pinky_dip = self.joint_angle(

            landmarks[18],

            landmarks[19],

            landmarks[20],

        )

        return JointAngles(

            wrist,

            thumb_mcp,

            thumb_ip,

            index_mcp,

            index_pip,

            index_dip,

            middle_mcp,

            middle_pip,

            middle_dip,

            ring_mcp,

            ring_pip,

            ring_dip,

            pinky_mcp,

            pinky_pip,

            pinky_dip,

        )

    # -----------------------------------------------------

    @staticmethod
    def relative_rotation(

        parent_rotation,

        child_rotation,

    ):

        """
        Relative rotation matrix.
        """

        return parent_rotation.T @ child_rotation

    # -----------------------------------------------------

    @staticmethod
    def quaternion_angle(

        q_parent,

        q_child,

    ):

        """
        Joint angle using quaternions.
        """

        r1 = Rotation.from_quat(q_parent)

        r2 = Rotation.from_quat(q_child)

        relative = r1.inv() * r2

        return np.degrees(

            relative.magnitude()

        )

    # -----------------------------------------------------

    def marker_angles(

        self,

        marker_dictionary: Dict,

        finger_layout: Dict[str, List[int]],

    ):

        """
        Computes angles between consecutive
        ArUco markers.

        Example

        Index

        MCP Marker

        PIP Marker

        DIP Marker
        """

        angles = {}

        for finger, ids in finger_layout.items():

            finger_angles = []

            for i in range(len(ids) - 1):

                q1 = marker_dictionary[
                    ids[i]
                ].quaternion

                q2 = marker_dictionary[
                    ids[i + 1]
                ].quaternion

                finger_angles.append(

                    self.quaternion_angle(

                        q1,

                        q2,

                    )

                )

            angles[finger] = finger_angles

        return angles

    # -----------------------------------------------------

    @staticmethod
    def to_dictionary(

        joint_angles: JointAngles,

    ):

        """
        Dataclass → Dictionary
        """

        return vars(joint_angles)