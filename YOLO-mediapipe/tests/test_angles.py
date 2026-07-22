"""
Unit tests for src.geometry.angle_calculator.AngleCalculator.

Run with:
    pytest tests/test_angles.py
"""

import numpy as np
import pytest

from src.geometry.angle_calculator import AngleCalculator, JointAngles


def test_joint_angle_straight_line_is_180_degrees():
    # p1 -- p2 -- p3 all on one straight line -> fully extended joint
    p1 = (0, 0)
    p2 = (1, 0)
    p3 = (2, 0)

    angle = AngleCalculator.joint_angle(p1, p2, p3)

    assert angle == pytest.approx(180.0, abs=1e-6)


def test_joint_angle_right_angle_is_90_degrees():
    p1 = (1, 0)
    p2 = (0, 0)
    p3 = (0, 1)

    angle = AngleCalculator.joint_angle(p1, p2, p3)

    assert angle == pytest.approx(90.0, abs=1e-6)


def test_joint_angle_folded_back_is_0_degrees():
    # p1 and p3 on the same side of p2 -> fully folded joint
    p1 = (1, 0)
    p2 = (0, 0)
    p3 = (1, 0)

    angle = AngleCalculator.joint_angle(p1, p2, p3)

    assert angle == pytest.approx(0.0, abs=1e-6)


def test_angle_between_orthogonal_vectors():
    v1 = np.array([1, 0])
    v2 = np.array([0, 1])

    assert AngleCalculator.angle_between(v1, v2) == pytest.approx(90.0, abs=1e-6)


def test_compute_from_landmarks_returns_joint_angles_for_straight_fingers():
    # 21 MediaPipe hand landmarks, all fingers extended straight upward
    # from the wrist. Exact positions are not anatomically realistic --
    # only collinearity per finger matters for this test.
    landmarks = [(0, 0)] * 21

    landmarks[0] = (0, 0)     # wrist
    for finger_base, count in [(1, 4), (5, 4), (9, 4), (13, 4), (17, 4)]:
        for i in range(count):
            landmarks[finger_base + i] = (finger_base, -(i + 1))

    calculator = AngleCalculator()
    angles = calculator.compute_from_landmarks(landmarks)

    assert isinstance(angles, JointAngles)
    # A straight finger's PIP/DIP joints should read close to 180 degrees.
    assert angles.index_pip == pytest.approx(180.0, abs=1e-6)
    assert angles.middle_pip == pytest.approx(180.0, abs=1e-6)


def test_to_dictionary_matches_dataclass_fields():
    calculator = AngleCalculator()
    landmarks = [(i, 0) for i in range(21)]

    angles = calculator.compute_from_landmarks(landmarks)
    as_dict = calculator.to_dictionary(angles)

    assert set(as_dict.keys()) == set(angles.__dataclass_fields__.keys())
