import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cube_tracking.geometry import (  # noqa: E402
    average_quaternions,
    get_cube_and_face,
    is_quaternion_perpendicular,
)


@pytest.mark.parametrize("marker_id,expected_cube,expected_face", [
    (0, 0, 'Top'),
    (1, 0, 'Front'),
    (5, 0, 'Bottom'),
    (6, 1, 'Top'),
    (11, 1, 'Bottom'),
    (12, 2, 'Top'),
])
def test_get_cube_and_face(marker_id, expected_cube, expected_face):
    cube_idx, face = get_cube_and_face(marker_id)
    assert cube_idx == expected_cube
    assert face == expected_face


def test_average_quaternions_identical_inputs():
    q = np.array([0.0, 0.0, 0.0, 1.0])
    result = average_quaternions([q, q, q])
    # Result should be parallel to the input (sign may flip).
    assert np.allclose(np.abs(result), np.abs(q), atol=1e-6)


def test_average_quaternions_returns_unit_quaternion():
    quats = [
        np.array([0.0, 0.0, 0.0, 1.0]),
        np.array([0.0, 0.0, 0.1, 0.995]),
        np.array([0.0, 0.05, 0.0, 0.9987]),
    ]
    quats = [q / np.linalg.norm(q) for q in quats]
    result = average_quaternions(quats)
    assert np.isclose(np.linalg.norm(result), 1.0, atol=1e-6)


def test_is_quaternion_perpendicular_identity_is_false():
    identity_quat = np.array([0.0, 0.0, 0.0, 1.0])
    assert not is_quaternion_perpendicular(identity_quat)
