"""
Rendering/overlay drawing for tracked cubes.

Purely a function of already-computed pose data — contains no tracking
or detection logic, so tracking could run headless without this module.
"""

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

from .config import BASE_CUBE_PIXEL_SIZE, CUBE_COLORS, EDGE_PAIRS, VECTOR_COLORS

FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_3d_cube(frame: np.ndarray, center: tuple[int, int],
                  quat: np.ndarray, faces: list[str],
                  cube_idx: int, averaged: bool) -> None:
    """Render a wireframe cube and face markers on the frame."""
    half = BASE_CUBE_PIXEL_SIZE // 2
    vertices = np.array([
        [-half, -half, -half], [half, -half, -half],
        [half, half, -half], [-half, half, -half],
        [-half, -half, half], [half, -half, half],
        [half, half, half], [-half, half, half],
    ])
    rot = R.from_quat(quat)
    pts = rot.apply(vertices) + np.array([center[0], center[1], 0])
    projected = [tuple(map(int, p[:2])) for p in pts]

    for i, edge in enumerate(EDGE_PAIRS):
        color = list(CUBE_COLORS[cube_idx % len(CUBE_COLORS)])
        if i < 4:
            color = [int(c * 0.7) for c in color]
        cv2.line(frame, projected[edge[0]], projected[edge[1]], color, 2)

    face_pos_idx = {'Front': 4, 'Back': 0, 'Left': 3, 'Right': 1, 'Top': 5, 'Bottom': 2}
    for face in faces:
        idx = face_pos_idx[face]
        cv2.circle(frame, projected[idx], 8, (255, 255, 255), -1)
        cv2.putText(
            frame, face[0],
            (projected[idx][0] + 5, projected[idx][1] + 5),
            FONT, 0.5, (0, 0, 0), 1
        )

    cv2.putText(
        frame, str(cube_idx),
        (center[0] - 10, center[1] + 5),
        FONT, 0.8, (255, 255, 255), 2, cv2.LINE_AA
    )


def draw_vector_arrows(frame: np.ndarray, center: tuple[int, int],
                        quat: np.ndarray, length: int = 40) -> None:
    """Draw X, Y, Z axes as arrows from center point."""
    rot = R.from_quat(quat)
    axes = np.eye(3) * length
    pts = rot.apply(axes) + np.array([center[0], center[1], 0])

    for i, pt in enumerate(pts):
        end = tuple(map(int, pt[:2]))
        cv2.arrowedLine(frame, center, end, VECTOR_COLORS[i], 3, tipLength=0.3)
        cv2.arrowedLine(frame, center, end, (0, 0, 0), 1, tipLength=0.3)
        label = ['X', 'Y', 'Z'][i]
        sz = cv2.getTextSize(label, FONT, 0.6, 1)[0]
        cv2.rectangle(
            frame,
            (end[0] + 3, end[1] - sz[1] - 3),
            (end[0] + sz[0] + 6, end[1] + 3),
            (0, 0, 0), -1
        )
        cv2.putText(frame, label, (end[0] + 5, end[1]), FONT, 0.6, VECTOR_COLORS[i], 1)


def draw_info_panel(frame: np.ndarray, cube_idx: int,
                     position: tuple[float, float, float],
                     quat: np.ndarray, faces: list[str],
                     averaged: bool) -> None:
    """Draw a textual overlay with cube status."""
    base_y = 40 + cube_idx * 120
    bg = (60, 60, 60) if cube_idx % 2 == 0 else (40, 40, 40)
    cv2.rectangle(frame, (10, base_y - 20), (320, base_y + 100), bg, -1)

    header = f"Cube {cube_idx} ({len(faces)} faces)"
    color = (255, 255, 0) if averaged else (200, 200, 200)
    cv2.putText(frame, header, (15, base_y), FONT, 0.6, color, 1)

    pos_text = f"X:{position[0]:.1f}cm  Y:{position[1]:.1f}cm  Z:{position[2]:.1f}cm"
    if averaged:
        pos_text += " (Averaged)"
    cv2.putText(frame, pos_text, (15, base_y + 25), FONT, 0.5, (255, 255, 0), 1)

    cv2.putText(frame, "Orientation:", (15, base_y + 45), FONT, 0.5, (255, 255, 255), 1)
    q_str = f"[{quat[0]:.2f}, {quat[1]:.2f}, {quat[2]:.2f}, {quat[3]:.2f}]"
    cv2.putText(frame, q_str, (15, base_y + 65), FONT, 0.4, (255, 150, 255), 1)

    faces_str = "Visible: " + ", ".join(faces)
    cv2.putText(frame, faces_str, (15, base_y + 85), FONT, 0.5, (200, 200, 0), 1)


def draw_fps(frame: np.ndarray, fps: float) -> None:
    """Draw the current FPS counter in the top-left corner."""
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), FONT, 0.7, (0, 255, 0), 2)
