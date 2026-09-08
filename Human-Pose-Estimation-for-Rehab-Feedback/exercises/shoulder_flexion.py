# exercises/shoulder_flexion.py
import time
from exercises.base import BaseExerciseChecker
from utils.angles import angle_between_3d
from utils.smoothing import SimpleSmoother
from utils.landmarks import landmarks_to_dict
import math

class ShoulderFlexionChecker(BaseExerciseChecker):
    """
    Upgraded shoulder flexion checker with both-arm support, elbow/trunk checks, and progress.
    Config keys:
      side: "right" | "left" | "both"
      target_angle_up, target_angle_down, tolerance_deg, hold_time_sec, smoothing_window, min_moving_angle
      max_elbow_flexion_deg (max allowed elbow flexion; 0 means fully straight)
      max_torso_tilt_deg (max allowed torso tilt in degrees)
    """
    def __init__(self, config, logger=None):
        super().__init__("shoulder_flexion", config, logger)
        c = config
        self.side = c.get("side", "both").lower()
        self.target_up = float(c.get("target_angle_up", 160))
        self.target_down = float(c.get("target_angle_down", 40))
        self.tol = float(c.get("tolerance_deg", 30))
        self.hold_time = float(c.get("hold_time_sec", 5))
        self.smoother_window = int(c.get("smoothing_window", 7))
        self.min_moving_angle = float(c.get("min_moving_angle", 8))
        self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 20))
        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 20))

        # per-side smoothing and hold state
        self.smoothers = {"LEFT": SimpleSmoother(self.smoother_window), "RIGHT": SimpleSmoother(self.smoother_window)}
        self.hold_start = {"LEFT": None, "RIGHT": None}
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "down", "RIGHT": "down"}

    def _get_triplets(self, lm_dict):
        pairs = {}
        # returns hip, shoulder, elbow, wrist for each side if available
        if "RIGHT_SHOULDER" in lm_dict:
            pairs["RIGHT"] = {
                "hip": lm_dict.get("RIGHT_HIP"),
                "shoulder": lm_dict.get("RIGHT_SHOULDER"),
                "elbow": lm_dict.get("RIGHT_ELBOW"),
                "wrist": lm_dict.get("RIGHT_WRIST")
            }
        if "LEFT_SHOULDER" in lm_dict:
            pairs["LEFT"] = {
                "hip": lm_dict.get("LEFT_HIP"),
                "shoulder": lm_dict.get("LEFT_SHOULDER"),
                "elbow": lm_dict.get("LEFT_ELBOW"),
                "wrist": lm_dict.get("LEFT_WRIST")
            }
        return pairs

    def _torso_tilt(self, lm_dict):
        # estimate torso tilt from shoulders vs hips
        try:
            l_sh = lm_dict.get("LEFT_SHOULDER")
            r_sh = lm_dict.get("RIGHT_SHOULDER")
            l_hip = lm_dict.get("LEFT_HIP")
            r_hip = lm_dict.get("RIGHT_HIP")
            if not (l_sh and r_sh and l_hip and r_hip):
                return None
            # compute shoulder mid and hip mid
            sh_mid = ((l_sh[0]+r_sh[0])/2.0, (l_sh[1]+r_sh[1])/2.0, (l_sh[2]+r_sh[2])/2.0)
            hip_mid = ((l_hip[0]+r_hip[0])/2.0, (l_hip[1]+r_hip[1])/2.0, (l_hip[2]+r_hip[2])/2.0)
            # vector from hip_mid to sh_mid forms torso; measure angle from vertical (y-axis)
            vx = sh_mid[0] - hip_mid[0]
            vy = sh_mid[1] - hip_mid[1]
            # angle relative to vertical axis (0 means perfectly vertical)
            if vx == 0 and vy == 0:
                return 0.0
            # in normalized image coords, vertical is positive y; we compute tilt as arctan(|vx|/|vy|)
            tilt_rad = math.atan2(abs(vx), abs(vy) + 1e-8)
            tilt_deg = math.degrees(tilt_rad)
            return tilt_deg
        except Exception:
            return None

    def update(self, raw_landmarks, t=None):
        now = t or time.time()
        lm = landmarks_to_dict(raw_landmarks)
        if not lm:
            self.state = "no_pose"
            return {"status":"no_pose", "per_side": {}}

        torso_tilt = self._torso_tilt(lm)
        triplets = self._get_triplets(lm)
        results = {"per_side": {}, "torso_tilt_deg": torso_tilt}

        sides = []
        if self.side == "both":
            sides = ["LEFT","RIGHT"]
        elif self.side == "left":
            sides = ["LEFT"]
        else:
            sides = ["RIGHT"]

        for sd in sides:
            info = triplets.get(sd)
            if not info or not info.get("hip") or not info.get("shoulder") or not info.get("elbow") or not info.get("wrist"):
                results["per_side"][sd] = {"status":"no_pose"}
                continue

            hip = info["hip"]; sh = info["shoulder"]; el = info["elbow"]; wr = info["wrist"]

            # compute main shoulder flexion angle (hip - shoulder - elbow)
            ang = angle_between_3d(hip, sh, el)
            ang_s = self.smoothers[sd].update(ang)

            # compute elbow flexion (shoulder - elbow - wrist) -> want close to 180
            elbow_ang = angle_between_3d(sh, el, wr)
            elbow_flexion = 180.0 - elbow_ang  # how much it is bent; 0 ideal

            # errors
            reasons = []
            ok = False

            # check torso tilt
            if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt}°")

            # elbow straightness check
            if elbow_flexion > self.max_elbow_flexion:
                reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion}°")

            # check up / hold logic
            if ang_s >= self.target_up - self.tol:
                # candidate up position
                if self.hold_start[sd] is None:
                    self.hold_start[sd] = now
                elapsed = now - self.hold_start[sd]
                if elapsed >= self.hold_time:
                    # count rep only if last stage was not already up_done
                    if self.last_stage[sd] != "up_done":
                        self.reps[sd] += 1
                        self.log(f"{sd}_rep_done", self.reps[sd], note=f"ang={ang_s:.1f}")
                        self.last_stage[sd] = "up_done"
                    results["per_side"][sd] = {"status":"done", "angle": ang_s, "elbow_flexion": elbow_flexion,
                                               "reasons": reasons, "reps": self.reps[sd], "hold_elapsed": elapsed}
                else:
                    results["per_side"][sd] = {"status":"holding", "angle": ang_s, "elbow_flexion": elbow_flexion,
                                               "reasons": reasons, "hold_elapsed": elapsed}
            elif ang_s <= self.target_down + self.tol:
                # down position
                self.hold_start[sd] = None
                if self.last_stage[sd] == "up_done":
                    # returned down after counted up -> reset to allow next rep
                    self.last_stage[sd] = "down"
                results["per_side"][sd] = {"status":"down", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
            else:
                # moving
                self.hold_start[sd] = None
                if ang_s > self.min_moving_angle:
                    results["per_side"][sd] = {"status":"moving", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
                else:
                    results["per_side"][sd] = {"status":"idle", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}

        return results

    def progress_along_path(self, shoulder_xy, elbow_xy, frame_wh):
        """
        Compute a simple projection progress (0..1) from overhead->front given shoulder and elbow normalized coords.
        Returns (progress, overhead_point, front_point) where points are normalized (x,y).
        """
        w, h = frame_wh
        sx, sy = shoulder_xy
        ex, ey = elbow_xy
        # overhead and front approximations relative to shoulder
        overhead = (sx, max(0.02, sy - 0.45))
        front = (sx, min(0.98, sy + 0.25))
        # project
        ov = (overhead[0]*w, overhead[1]*h)
        fv = (front[0]*w, front[1]*h)
        ev = (ex*w, ey*h)
        import numpy as np
        v = np.array(fv) - np.array(ov)
        p = np.array(ev) - np.array(ov)
        denom = np.dot(v, v) + 1e-8
        t = float(np.dot(p, v) / denom)
        t_clamped = max(0.0, min(1.0, t))
        return t_clamped, overhead, front

