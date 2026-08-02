"""
Temporal smoothing / tracking-history state for each cube.
"""

from collections import defaultdict, deque

import numpy as np

from .config import BASE_SMOOTHING, HISTORY_LENGTH, MAX_Z_DELTA, PERPENDICULAR_SMOOTHING
from .geometry import is_quaternion_perpendicular


def new_cube_history() -> dict:
    """Factory for a single cube's rolling tracking history."""
    return {
        'positions': deque(maxlen=HISTORY_LENGTH),
        'orientations': deque(maxlen=HISTORY_LENGTH),
        'z_values': deque(maxlen=HISTORY_LENGTH),
        'previous_z': None,
        'visible_faces': set(),
    }


class CubeHistoryStore:
    """Holds and manages per-cube tracking history across frames."""

    def __init__(self):
        self._histories = defaultdict(new_cube_history)

    def __getitem__(self, cube_idx: int) -> dict:
        return self._histories[cube_idx]

    def items(self):
        return self._histories.items()

    def clear(self) -> None:
        """Reset tracking history for all cubes."""
        self._histories.clear()

    def smooth_z(self, cube_idx: int, raw_z: float, quat: np.ndarray) -> float:
        """
        Stabilize the z-axis value using history and adaptive smoothing.

        Args:
            cube_idx: Identifier of cube.
            raw_z: Latest measured Z distance.
            quat: Current orientation quaternion.

        Returns:
            Smoothed Z value.
        """
        history = self._histories[cube_idx]
        smoothing = (
            PERPENDICULAR_SMOOTHING if is_quaternion_perpendicular(quat)
            else BASE_SMOOTHING
        )

        if (
            history['previous_z'] is not None
            and abs(raw_z - history['previous_z']) > MAX_Z_DELTA
        ):
            raw_z = history['previous_z']

        smoothed = (
            raw_z if history['previous_z'] is None else
            history['previous_z'] * (1 - smoothing) + raw_z * smoothing
        )
        history['z_values'].append(smoothed)
        history['previous_z'] = smoothed
        return smoothed
