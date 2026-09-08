import json, os, time
import numpy as np
from utils.landmarks import landmarks_to_dict
from utils.angles import angle_between_3d
from visolus_adapter import PoseEstimator

CFG_PATH = "config.json"
RECORD_SECONDS = 20   # how long to record (patient should do ~10 good reps)

def collect_angles(pose, side="LEFT"):
    """Record shoulder flexion angles for given side."""
    print(f"Recording {RECORD_SECONDS}s of reps... please start exercise!")
    start = time.time()
    max_angles, min_angles = [], []

    cur_max, cur_min = -999, 999
    last_state = None

    while time.time() - start < RECORD_SECONDS:
        frame, lm_raw = pose.capture()
        lm = landmarks_to_dict(lm_raw)
        if not lm: continue

        hip = lm.get(f"{side}_HIP")
        sh  = lm.get(f"{side}_SHOULDER")
        el  = lm.get(f"{side}_ELBOW")
        if not (hip and sh and el): 
            continue

        ang = angle_between_3d(hip, sh, el)

        # detect peak / valley by simple threshold crossing
        state = "up" if ang > 100 else "down"
        if state != last_state and last_state is not None:
            if last_state == "up":
                max_angles.append(cur_max)
                cur_max = -999
            elif last_state == "down":
                min_angles.append(cur_min)
                cur_min = 999
        last_state = state
        cur_max = max(cur_max, ang)
        cur_min = min(cur_min, ang)

    return np.array(max_angles), np.array(min_angles)

def suggest_thresholds(max_angles, min_angles):
    mean_up, std_up = np.mean(max_angles), np.std(max_angles)
    mean_down, std_down = np.mean(min_angles), np.std(min_angles)

    suggested = {
        "target_angle_up": round(mean_up - 0.5*std_up),
        "target_angle_down": round(mean_down + 0.5*std_down),
        "tolerance_deg": max(8, round(1.5*max(std_up, std_down)))
    }
    return suggested

if __name__ == "__main__":
    pose = PoseEstimator()
    max_up, min_down = collect_angles(pose, side="LEFT")
    pose.close()

    print("Max angles:", max_up)
    print("Min angles:", min_down)

    if len(max_up) < 3 or len(min_down) < 3:
        print("Not enough reps recorded. Please retry.")
        exit(1)

    sugg = suggest_thresholds(max_up, min_down)
    print("Suggested params:", sugg)

    # write back to config.json
    if os.path.exists(CFG_PATH):
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}

    if "shoulder_flexion" not in cfg:
        cfg["shoulder_flexion"] = {}
    cfg["shoulder_flexion"].update(sugg)

    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    print("Updated config.json ✅")
