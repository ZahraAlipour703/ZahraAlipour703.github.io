# exercises/farmers_carry.py
import time, math
from exercises.base import BaseExerciseChecker
from utils.angles import angle_between_3d
from utils.landmarks import landmarks_to_dict

class FarmersCarryChecker(BaseExerciseChecker):
    """
    Farmer’s Carry (Seated) –
      The patient holds heavy weights in each hand while sitting upright.
      Goal is to maintain straight elbows and minimal torso sway for a set duration.
      This is an isometric endurance exercise.

    Config keys (farmers_carry):
      side: "both" | "left" | "right"
      max_elbow_flexion_deg: max allowed bend at elbow (default=20°)
      max_torso_tilt_deg: max allowed torso lean (default=15°)
      carry_duration_sec: required hold duration (default=20s)
      carry_min_ok_fraction: minimum % of time form must be correct (default=0.9)
    """

    def __init__(self, config, logger=None):
        super().__init__("farmers_carry", config, logger)
        c = config or {}
        self.side = c.get("side", "both").lower()
        self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 20))
        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 15))
        self.carry_duration = float(c.get("carry_duration_sec", 20))
        self.carry_min_ok_fraction = float(c.get("carry_min_ok_fraction", 0.9))

        # tracking state
        self.carry_start = None
        self.carry_ok_time = 0.0
        self.last_update_time = None

    def _get_triplets(self, dt):
        pairs = {}
        if "RIGHT_SHOULDER" in dt:
            pairs["RIGHT"] = {
                "hip": dt.get("RIGHT_HIP"),
                "shoulder": dt.get("RIGHT_SHOULDER"),
                "elbow": dt.get("RIGHT_ELBOW"),
                "wrist": dt.get("RIGHT_WRIST"),
            }
        if "LEFT_SHOULDER" in dt:
            pairs["LEFT"] = {
                "hip": dt.get("LEFT_HIP"),
                "shoulder": dt.get("LEFT_SHOULDER"),
                "elbow": dt.get("LEFT_ELBOW"),
                "wrist": dt.get("LEFT_WRIST"),
            }
        return pairs

    def _torso_tilt(self, dt):
        try:
            l_sh = dt.get("LEFT_SHOULDER"); r_sh = dt.get("RIGHT_SHOULDER")
            l_hip = dt.get("LEFT_HIP"); r_hip = dt.get("RIGHT_HIP")
            if not (l_sh and r_sh and l_hip and r_hip):
                return None
            sh_mid = ((l_sh[0]+r_sh[0])/2.0, (l_sh[1]+r_sh[1])/2.0)
            hip_mid = ((l_hip[0]+r_hip[0])/2.0, (l_hip[1]+r_hip[1])/2.0)
            vx = sh_mid[0] - hip_mid[0]
            vy = sh_mid[1] - hip_mid[1]
            tilt_rad = math.atan2(abs(vx), abs(vy) + 1e-8)
            return math.degrees(tilt_rad)
        except Exception:
            return None

    def update(self, raw_landmarks, t=None):
        now = t or time.time()

        # dt for fps-independent timing
        dt_time = 0.0
        if self.last_update_time is not None:
            dt_time = now - self.last_update_time
        self.last_update_time = now

        dt = landmarks_to_dict(raw_landmarks)
        if not dt:
            self.state = "no_pose"
            return {"status":"no_pose","per_side":{},"carry":{}}

        torso_tilt = self._torso_tilt(dt)
        triplets = self._get_triplets(dt)
        results = {"per_side": {}, "torso_tilt_deg": torso_tilt, "carry": {}}

        sides = ["LEFT","RIGHT"] if self.side == "both" else (
            ["LEFT"] if self.side == "left" else ["RIGHT"]
        )

        # initialize carry session
        if self.carry_start is None:
            self.carry_start = now
            self.carry_ok_time = 0.0

        for sd in sides:
            info = triplets.get(sd)
            if not info or not info["shoulder"] or not info["elbow"] or not info["wrist"]:
                results["per_side"][sd] = {"status":"no_pose"}
                continue

            sh, el, wr = info["shoulder"], info["elbow"], info["wrist"]

            # elbow flexion (shoulder-elbow-wrist)
            elbow_ang = angle_between_3d(sh, el, wr)
            elbow_flexion = max(0.0, 180.0 - elbow_ang)

            reasons = []
            if elbow_flexion > self.max_elbow_flexion:
                reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion}°")
            if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt}°")

            status = "ok" if len(reasons) == 0 else "bad_form"
            results["per_side"][sd] = {
                "status": status,
                "elbow_flexion": elbow_flexion,
                "reasons": reasons,
            }

            if status == "ok":
                self.carry_ok_time += dt_time

        # carry progress
        total_elapsed = now - self.carry_start
        ok_fraction = min(1.0, self.carry_ok_time / max(1e-6, total_elapsed))
        completed = (total_elapsed >= self.carry_duration) and (ok_fraction >= self.carry_min_ok_fraction)

        results["carry"] = {
            "elapsed": total_elapsed,
            "ok_time": self.carry_ok_time,
            "ok_fraction": ok_fraction,
            "required_duration": self.carry_duration,
            "completed": completed,
        }

        return results
