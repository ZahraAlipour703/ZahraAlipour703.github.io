# utils/reference_motion.py
"""
Reference motion generator for rehab exercises.
Each function returns a list of poses (dict of landmark_name -> (x,y,z) normalized coords)
that loop smoothly. The poses are compatible with the draw_skeleton helper.
"""

import numpy as np

def shoulder_flexion_reference(num_frames=120, side="LEFT"):
    """Full-body reference loop: arm forward flexion from ~40° -> ~160° and hold briefly."""
    poses = []
    for i, t in enumerate(np.linspace(0, 1, num_frames)):
        # create a smooth up-hold-down cycle: ease-in/out with pause near top
        cycle = (np.sin(2 * np.pi * t) * 0.5 + 0.5)  # smooth 0..1..0
        # bias to spend time near top: apply ease-power
        bias = cycle**1.4

        # angles in degrees: 40 -> 160
        angle = 40 + bias * (160 - 40)

        # base body positions (normalized)
        head = (0.50, 0.18, 0)
        left_sh = (0.42, 0.36, 0)
        right_sh = (0.58, 0.36, 0)
        left_hip = (0.46, 0.68, 0)
        right_hip = (0.54, 0.68, 0)
        left_knee = (0.46, 0.88, 0)
        left_ankle = (0.46, 0.98, 0)

        # arm geometry: rotate in sagittal plane (approximation)
        # compute elbow/wrist by projecting along vertical with cos(angle) influence
        # elbow drops in y as angle increases (arm goes up)
        elbow_y = left_sh[1] - 0.28 * np.cos(np.radians(angle))
        elbow_x = left_sh[0] + 0.02 * np.sin(np.radians(angle))
        wrist_y = elbow_y - 0.24
        wrist_x = elbow_x + 0.01

        left_el = (elbow_x, elbow_y, 0)
        left_wr = (wrist_x, wrist_y, 0)

        # little natural counter-movement on the other side (arm not animated fully)
        right_el = (right_sh[0] + 0.02, right_sh[1] + 0.08, 0)
        right_wr = (right_el[0] + 0.02, right_el[1] + 0.22, 0)

        pose = {
            "NOSE": (0.50, 0.14, 0),
            "LEFT_SHOULDER": left_sh,
            "RIGHT_SHOULDER": right_sh,
            "LEFT_ELBOW": left_el,
            "RIGHT_ELBOW": right_el,
            "LEFT_WRIST": left_wr,
            "RIGHT_WRIST": right_wr,
            "LEFT_HIP": left_hip,
            "RIGHT_HIP": right_hip,
            "LEFT_KNEE": left_knee,
            "LEFT_ANKLE": left_ankle,
            "HEAD": head,
        }
        poses.append(pose)
    return poses


def farmers_carry_reference(num_frames=120):
    """Reference loop for farmer's carry: arms down holding weight with small sway."""
    poses = []
    for t in np.linspace(0, 1, num_frames):
        sway = np.sin(2 * np.pi * t) * 0.03  # small lateral sway
        head = (0.50 + sway * 0.2, 0.18, 0)
        left_sh = (0.45 + sway, 0.36, 0)
        right_sh = (0.55 + sway, 0.36, 0)
        left_wr = (left_sh[0], 0.88, 0)
        right_wr = (right_sh[0], 0.88, 0)
        left_hip = (0.47 + sway * 0.2, 0.68, 0)
        right_hip = (0.53 + sway * 0.2, 0.68, 0)

        pose = {
            "NOSE": (0.5, 0.14, 0),
            "LEFT_SHOULDER": left_sh,
            "RIGHT_SHOULDER": right_sh,
            "LEFT_WRIST": left_wr,
            "RIGHT_WRIST": right_wr,
            "LEFT_HIP": left_hip,
            "RIGHT_HIP": right_hip,
            "LEFT_KNEE": (left_hip[0], 0.88, 0),
            "LEFT_ANKLE": (left_hip[0], 0.98, 0)
        }
        poses.append(pose)
    return poses


def arm_raise_and_carry_reference(num_frames=120):
    """Combined reference: one arm raises (side or front depending) while the other carries."""
    poses = []
    for t in np.linspace(0, 1, num_frames):
        cycle = (np.sin(2 * np.pi * t) * 0.5 + 0.5)
        # For combined behaviour we animate an abduction (side raise) up to ~90deg
        angle = cycle * 90.0  # 0..90
        head = (0.5, 0.18, 0)
        left_sh = (0.45, 0.36, 0)
        right_sh = (0.55, 0.36, 0)
        # compute left arm swinging sideways/outward:
        elbow_x = left_sh[0] - 0.25 * np.cos(np.radians(angle))
        elbow_y = left_sh[1] - 0.25 * np.sin(np.radians(angle))
        wrist_x = elbow_x - 0.18 * np.cos(np.radians(angle))
        wrist_y = elbow_y - 0.18 * np.sin(np.radians(angle))

        # other arm stays down carrying (small sway)
        other_wrist = (right_sh[0] + 0.02 * np.sin(2*np.pi*t), 0.88, 0)

        pose = {
            "NOSE": (0.50, 0.14, 0),
            "LEFT_SHOULDER": left_sh,
            "RIGHT_SHOULDER": right_sh,
            "LEFT_ELBOW": (elbow_x, elbow_y, 0),
            "LEFT_WRIST": (wrist_x, wrist_y, 0),
            "RIGHT_WRIST": other_wrist,
            "LEFT_HIP": (0.47, 0.68, 0),
            "RIGHT_HIP": (0.53, 0.68, 0),
        }
        poses.append(pose)
    return poses

def mini_squat_reference(num_frames=120):
    """Reference squat cycle: stand -> squat -> stand"""
    poses = []
    for t in np.linspace(0, 1, num_frames):
        cycle = (np.sin(2 * np.pi * t) * 0.5 + 0.5)  # 0..1..0
        angle = 170 - cycle * 100  # knee flexion 170 -> 70 deg approx

        hip_y = 0.68 + cycle * 0.12
        knee_y = 0.88
        ankle_y = 0.98

        left_hip = (0.46, hip_y, 0)
        right_hip = (0.54, hip_y, 0)
        left_knee = (0.46, knee_y, 0)
        right_knee = (0.54, knee_y, 0)
        left_ankle = (0.46, ankle_y, 0)
        right_ankle = (0.54, ankle_y, 0)

        pose = {
            "LEFT_HIP": left_hip,
            "RIGHT_HIP": right_hip,
            "LEFT_KNEE": left_knee,
            "RIGHT_KNEE": right_knee,
            "LEFT_ANKLE": left_ankle,
            "RIGHT_ANKLE": right_ankle,
        }
        poses.append(pose)
    return poses



# mapping used by run_local.py to pick correct reference
REFERENCE_FUNCTIONS = {
    "shoulder_flexion": shoulder_flexion_reference,
    "farmers_carry": farmers_carry_reference,
    "arm_raise_and_carry": arm_raise_and_carry_reference,
    # also allow alternate key
    "shoulder_abduction": arm_raise_and_carry_reference,
    "mini_squat" : mini_squat_reference,
}
