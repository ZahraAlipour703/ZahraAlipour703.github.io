# # # utils/draw.py
# import cv2

# # simple list of useful connections (subset of MediaPipe pose connections)
# DEFAULT_CONNECTIONS = [
#     ("NOSE", "LEFT_SHOULDER"),
#     ("NOSE", "RIGHT_SHOULDER"),
#     ("LEFT_SHOULDER", "LEFT_ELBOW"),
#     ("LEFT_ELBOW", "LEFT_WRIST"),
#     ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
#     ("RIGHT_ELBOW", "RIGHT_WRIST"),
#     ("LEFT_SHOULDER", "LEFT_HIP"),
#     ("RIGHT_SHOULDER", "RIGHT_HIP"),
#     ("LEFT_HIP", "LEFT_KNEE"),
#     ("LEFT_KNEE", "LEFT_ANKLE")
# ]


# def draw_skeleton(frame, landmarks, color=(200, 200, 200), thickness=3, connections=None):
#     """
#     Draw skeleton on `frame` given `landmarks` dict with normalized coords (x,y,z).
#     - landmarks: {"LEFT_SHOULDER": (x,y,z), ...}
#     - color: BGR tuple
#     """
#     if connections is None:
#         connections = DEFAULT_CONNECTIONS
#     h, w = frame.shape[:2]

#     # draw bones
#     for a, b in connections:
#         if a in landmarks and b in landmarks:
#             ax, ay, _ = landmarks[a]
#             bx, by, _ = landmarks[b]
#             pt_a = (int(ax * w), int(ay * h))
#             pt_b = (int(bx * w), int(by * h))
#             cv2.line(frame, pt_a, pt_b, color, thickness, lineType=cv2.LINE_AA)

#     # draw joints
#     for name, (x, y, _) in landmarks.items():
#         cx, cy = int(x * w), int(y * h)
#         cv2.circle(frame, (cx, cy), 5, (255, 255, 0), -1)  # bright marker


# def overlay_reference_corner(frame, ref_pose, size_px=220, bg_color=(30, 30, 30),
#                              label=None, label_color=(255,255,255)):
#     """
#     Render a small reference skeleton in a corner (returns frame with overlay applied in-place).
#     - ref_pose: dict of normalized landmarks
#     - size_px: size of square overlay
#     - label: optional string rendered under the overlay
#     """
#     h, w = frame.shape[:2]
#     # prepare blank canvas for small overlay
#     canvas = 255 * np.ones((size_px, size_px, 3), dtype='uint8')
#     canvas[:] = bg_color

#     # scale landmarks to canvas (we'll re-normalize coords to the canvas)
#     # draw_skeleton expects normalized coords, so adapt by drawing on temporary canvas
#     tmp = canvas.copy()
#     draw_skeleton(tmp, ref_pose, color=(220,220,220), thickness=2)

#     # add helpful arrows/teaching cues for shoulder flexion / abduction types:
#     # try to draw an arrow from shoulder to wrist if landmarks present
#     try:
#         if "LEFT_SHOULDER" in ref_pose and "LEFT_WRIST" in ref_pose:
#             sx, sy, _ = ref_pose["LEFT_SHOULDER"]
#             wx, wy, _ = ref_pose["LEFT_WRIST"]
#             p1 = (int(sx * size_px), int(sy * size_px))
#             p2 = (int(wx * size_px), int(wy * size_px))
#             cv2.arrowedLine(tmp, p1, p2, (100, 200, 255), 2, tipLength=0.25)
#     except Exception:
#         pass

#     # place overlay top-left
#     frame[10:10+size_px, 10:10+size_px] = tmp

#     # label
#     if label:
#         cv2.putText(frame, label, (12, 10+size_px+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_color, 2)

# # we use numpy here (import inside file to avoid top-level import issues)
# import numpy as np

#second version yolov8n pose
# utils/draw.py# utils/draw.py# utils/draw.py
# # utils/draw.py# utils/draw.pyimport cv2import cv2
import math
import numpy as np
import cv2
# COCO keypoint pairs for skeleton
COCO17_PAIRS = [
    (0, 1), (1, 2), (2, 3), (3, 4),      # Right arm
    (0, 5), (5, 6), (6, 7), (7, 8),      # Left arm
    (5, 11), (6, 12),                    # Shoulders to hips
    (11, 12),                            # Hip line
    (11, 13), (13, 15),                  # Left leg
    (12, 14), (14, 16),                  # Right leg
    (0, 17), (5, 17), (6, 17)            # Head/neck connections
]

def draw_skeleton(img, landmarks, color=(0, 255, 0), thickness=2, radius=4, exercise=None):
    """
    Draw skeleton given landmarks (dict {name: (x,y,z)} normalized).
    """
    if not landmarks:
        return

    h, w = img.shape[:2]

    # Convert to pixel coords
    pts = {}
    for name, (x, y, z) in landmarks.items():
        pts[name] = (int(x * w), int(y * h))

    # Draw connections (basic: shoulders, hips, knees, ankles, elbows, wrists)
    key_pairs = [
        ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
        ("LEFT_HIP", "RIGHT_HIP"),
        ("LEFT_SHOULDER", "LEFT_ELBOW"),
        ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
        ("LEFT_ELBOW", "LEFT_WRIST"),
        ("RIGHT_ELBOW", "RIGHT_WRIST"),
        ("LEFT_HIP", "LEFT_KNEE"),
        ("RIGHT_HIP", "RIGHT_KNEE"),
        ("LEFT_KNEE", "LEFT_ANKLE"),
        ("RIGHT_KNEE", "RIGHT_ANKLE"),
        ("LEFT_SHOULDER", "LEFT_HIP"),
        ("RIGHT_SHOULDER", "RIGHT_HIP"),
    ]

    for a, b in key_pairs:
        if a in pts and b in pts:
            cv2.line(img, pts[a], pts[b], color, thickness)

    # Draw joints
    for name, (px, py) in pts.items():
        cv2.circle(img, (px, py), radius, color, -1)


def draw_angle_on_image(img, landmarks, p1, p2, p3, color=(0,255,255)):
    """
    Draw angle at joint p2 formed by (p1 - p2 - p3).
    Returns angle in degrees or None if missing landmarks.
    """
    if not (p1 in landmarks and p2 in landmarks and p3 in landmarks):
        return None

    h, w = img.shape[:2]
    x1, y1, _ = landmarks[p1]
    x2, y2, _ = landmarks[p2]
    x3, y3, _ = landmarks[p3]

    p1_xy = (int(x1 * w), int(y1 * h))
    p2_xy = (int(x2 * w), int(y2 * h))
    p3_xy = (int(x3 * w), int(y3 * h))

    # vectors
    v1 = (p1_xy[0] - p2_xy[0], p1_xy[1] - p2_xy[1])
    v2 = (p3_xy[0] - p2_xy[0], p3_xy[1] - p2_xy[1])

    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2) + 1e-6
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2) + 1e-6
    cosang = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    angle = math.degrees(math.acos(cosang))

    # draw lines and points
    cv2.circle(img, p1_xy, 5, color, -1)
    cv2.circle(img, p2_xy, 6, (255,255,255), -1)  # center point highlighted
    cv2.circle(img, p3_xy, 5, color, -1)
    cv2.line(img, p2_xy, p1_xy, color, 2)
    cv2.line(img, p2_xy, p3_xy, color, 2)

    # angle text
    cv2.putText(img, f"{int(angle)}°", (p2_xy[0]+10, p2_xy[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

    return angle


def overlay_reference_corner(img, ref_landmarks, size_px=160, label="Coach", label_color=(255,255,255)):
    """
    Overlay small reference skeleton in bottom-right corner with transparent background.
    """
    h, w = img.shape[:2]
    scale = size_px

    # Create transparent canvas
    ref_img = np.ones((size_px, size_px, 4), dtype=np.uint8) * 0

    pts = {}
    for name, (x, y, z) in ref_landmarks.items():
        px = int(x * scale)
        py = int(y * scale)
        pts[name] = (px, py)

    # Draw skeleton on transparent canvas
    for a, b in [
        ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
        ("LEFT_HIP", "RIGHT_HIP"),
        ("LEFT_SHOULDER", "LEFT_ELBOW"),
        ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
        ("LEFT_ELBOW", "LEFT_WRIST"),
        ("RIGHT_ELBOW", "RIGHT_WRIST"),
        ("LEFT_HIP", "LEFT_KNEE"),
        ("RIGHT_HIP", "RIGHT_KNEE"),
        ("LEFT_KNEE", "LEFT_ANKLE"),
        ("RIGHT_KNEE", "RIGHT_ANKLE"),
        ("LEFT_SHOULDER", "LEFT_HIP"),
        ("RIGHT_SHOULDER", "RIGHT_HIP"),
    ]:
        if a in pts and b in pts:
            cv2.line(ref_img, pts[a], pts[b], (0,200,200,255), 2)

    for name, (px, py) in pts.items():
        cv2.circle(ref_img, (px, py), 4, (0,255,0,255), -1)

    # Alpha blend bottom-right
    x0, y0 = w - size_px - 10, h - size_px - 10
    overlay_roi = img[y0:y0+size_px, x0:x0+size_px]
    mask = ref_img[...,3:] / 255.0
    overlay_roi[:] = (1 - mask) * overlay_roi + mask * ref_img[...,:3]

    # Label
    cv2.putText(img, label, (x0, y0-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, label_color, 2, cv2.LINE_AA)
#----------------------------------------------====import cv2
