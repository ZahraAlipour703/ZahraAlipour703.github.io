import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cube_tracking.smoothing import CubeHistoryStore  # noqa: E402

IDENTITY_QUAT = np.array([0.0, 0.0, 0.0, 1.0])


def test_smooth_z_first_frame_returns_raw_value():
    store = CubeHistoryStore()
    result = store.smooth_z(cube_idx=0, raw_z=0.5, quat=IDENTITY_QUAT)
    assert result == 0.5


def test_smooth_z_rejects_large_jump():
    store = CubeHistoryStore()
    store.smooth_z(cube_idx=0, raw_z=0.5, quat=IDENTITY_QUAT)
    # A jump far larger than MAX_Z_DELTA should be clamped toward the previous value.
    result = store.smooth_z(cube_idx=0, raw_z=5.0, quat=IDENTITY_QUAT)
    assert result < 1.0  # nowhere near the outlier raw_z of 5.0


def test_smooth_z_converges_toward_stable_input():
    store = CubeHistoryStore()
    z = 0.3
    result = z
    for _ in range(50):
        result = store.smooth_z(cube_idx=0, raw_z=z, quat=IDENTITY_QUAT)
    assert np.isclose(result, z, atol=1e-3)


def test_clear_resets_all_histories():
    store = CubeHistoryStore()
    store.smooth_z(cube_idx=0, raw_z=0.5, quat=IDENTITY_QUAT)
    store.clear()
    assert store[0]['previous_z'] is None
