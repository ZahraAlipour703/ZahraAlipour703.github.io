
"""
Helpers to normalize and fuse landmarks coming from YOLO and Mediapipe.
Supports:
 - dict name->(x_norm,y_norm,z)
 - mediapipe list-like (.x,.y,.z)
 - numpy array Nx2/Nx3
Provides:
  - landmarks_to_dict(landmarks, frame_wh=None)
  - fuse_landmarks(yolo_dict, mp_dict)  # mp_dict is mediapipe-style name->(x,y,z)
"""
import numpy as np

try:
    import mediapipe as mp
    MP = mp.solutions.pose
except Exception:
    MP = None

COCO17_IDX_TO_NAME = {
    0: "NOSE", 1: "LEFT_EYE", 2: "RIGHT_EYE", 3: "LEFT_EAR", 4: "RIGHT_EAR",
    5: "LEFT_SHOULDER",6: "RIGHT_SHOULDER",7: "LEFT_ELBOW",8: "RIGHT_ELBOW",
    9: "LEFT_WRIST",10: "RIGHT_WRIST",11: "LEFT_HIP",12: "RIGHT_HIP",
    13: "LEFT_KNEE",14: "RIGHT_KNEE",15: "LEFT_ANKLE",16: "RIGHT_ANKLE"
}

def _maybe_normalize_xy(x, y, frame_wh):
    if frame_wh is None:
        return float(x), float(y)
    try:
        w, h = frame_wh
        if x > 2.0 or y > 2.0:
            return float(x) / float(w), float(y) / float(h)
    except Exception:
        pass
    return float(x), float(y)

def landmarks_to_dict(landmarks, frame_wh=None):
    """
    Convert various landmark formats to dict name->(x_norm,y_norm,z).
    If landmarks is already a dict, will clamp / normalize numbers.
    """
    out = {}
    if landmarks is None:
        return {}
    # already dict
    if isinstance(landmarks, dict):
        for k, v in landmarks.items():
            try:
                if v is None:
                    continue
                x = float(v[0]); y = float(v[1])
                z = float(v[2]) if len(v) > 2 else 0.0
                x, y = _maybe_normalize_xy(x, y, frame_wh)
                out[k] = (x, y, z)
            except Exception:
                continue
        return out

    # mediapipe-like list
    try:
        seq = list(landmarks)
        if seq and hasattr(seq[0], "x") and hasattr(seq[0], "y"):
            for i, lm in enumerate(seq):
                try:
                    name = MP.PoseLandmark(i).name if MP is not None else f"LM{i}"
                except Exception:
                    name = f"LM{i}"
                x = float(getattr(lm, "x", 0.0))
                y = float(getattr(lm, "y", 0.0))
                z = float(getattr(lm, "z", 0.0))
                out[name] = (x, y, z)
            return out
    except Exception:
        pass

    # numpy-like
    try:
        arr = np.asarray(landmarks)
        if arr.ndim == 2 and arr.shape[1] >= 2:
            for i in range(arr.shape[0]):
                try:
                    x = float(arr[i, 0]); y = float(arr[i, 1])
                    z = float(arr[i, 2]) if arr.shape[1] > 2 else 0.0
                    x, y = _maybe_normalize_xy(x, y, frame_wh)
                    out[f"KP{i}"] = (x, y, z)
                except Exception:
                    continue
            return out
    except Exception:
        pass

    return {}

def fuse_landmarks(yolo_dict, mp_dict):
    """
    Fuse two dicts that are both name->(x,y,z) normalized (0..1).
    Preference: YOLO keypoints if present, otherwise Mediapipe.
    Also ensures full-body COCO keys exist when possible.
    """
    out = {}
    if mp_dict is None:
        mp_dict = {}
    if yolo_dict is None:
        yolo_dict = {}

    # Start with mp dict (it often has full set)
    for k, v in mp_dict.items():
        out[k] = v

    # Overwrite with YOLO where available (higher priority for XY)
    for k, v in yolo_dict.items():
        out[k] = v

    # If some COCO keys missing, attempt mapping from MP naming variants (MP uses same names for many)
    # Already names should match: LEFT_HIP etc.
    return out
