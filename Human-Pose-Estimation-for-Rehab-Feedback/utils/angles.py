# utils/angles.py
import numpy as np

def angle_between_3d(a, b, c):
    """
    3D angle at point b between vectors ba and bc.
    a, b, c are (x,y) or (x,y,z)
    Returns angle in degrees.
    """
    a = np.array(a[:3], dtype=float)
    b = np.array(b[:3], dtype=float)
    c = np.array(c[:3], dtype=float)

    ba = a - b
    bc = c - b

    denom = (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosang = np.dot(ba, bc) / denom
    cosang = float(np.clip(cosang, -1.0, 1.0))
    ang = float(np.degrees(np.arccos(cosang)))
    return ang

# ✅ alias for backward compatibility
def angle_3pts(a, b, c):
    return angle_between_3d(a, b, c)
