import time, math
from exercises.base import BaseExerciseChecker
from utils.angles import angle_between_3d
from utils.smoothing import SimpleSmoother
from utils.landmarks import landmarks_to_dict


class ShoulderAbductionChecker(BaseExerciseChecker):
    """
    Shoulder abduction (lateral arm raise) checker.

    Behavior matches the project's other exercise checkers:
      - configurable targets and tolerances via config.json
      - per-side smoothing and hold/rep logic
      - elbow straightness + torso tilt form checks
      - friendly statuses: idle, moving, holding, done, holding_bad_form, down

    Config keys (under "shoulder_abduction"):
      side: "both" | "left" | "right"
      target_angle_up: (deg, default 160)
      target_angle_down: (deg, default 20)
      tolerance_deg: (deg tolerance, default 18)
      hold_time_sec: (seconds at top required to count, default 1.5)
      smoothing_window: (frames for smoother, default 7)
      min_moving_angle: (ignore tiny movement, default 8)
      max_elbow_flexion_deg: (allowed elbow bend, default 20)
      max_torso_tilt_deg: (allowed torso tilt, default 12)
    """

    def __init__(self, config, logger=None):
        super().__init__("shoulder_abduction", config, logger)
        c = config or {}
        self.side = c.get("side", "both").lower()
        # targets and thresholds
        self.target_up = float(c.get("target_angle_up", 160))
        self.target_down = float(c.get("target_angle_down", 20))
        self.tol = float(c.get("tolerance_deg", 18))
        self.hold_time = float(c.get("hold_time_sec", 1.5))
        self.smoother_window = int(c.get("smoothing_window", 7))
        self.min_moving_angle = float(c.get("min_moving_angle", 8))
        self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 20))
        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 12))

        # state
        self.smoothers = {
            "LEFT": SimpleSmoother(self.smoother_window),
            "RIGHT": SimpleSmoother(self.smoother_window)
        }
        self.hold_start = {"LEFT": None, "RIGHT": None}
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "down", "RIGHT": "down"}

    def _get_triplets(self, lm_dict):
        pairs = {}
        if "RIGHT_SHOULDER" in lm_dict:
            pairs["RIGHT"] = {
                "hip": lm_dict.get("RIGHT_HIP"),
                "shoulder": lm_dict.get("RIGHT_SHOULDER"),
                "elbow": lm_dict.get("RIGHT_ELBOW"),
                "wrist": lm_dict.get("RIGHT_WRIST"),
            }
        if "LEFT_SHOULDER" in lm_dict:
            pairs["LEFT"] = {
                "hip": lm_dict.get("LEFT_HIP"),
                "shoulder": lm_dict.get("LEFT_SHOULDER"),
                "elbow": lm_dict.get("LEFT_ELBOW"),
                "wrist": lm_dict.get("LEFT_WRIST"),
            }
        return pairs

    def _torso_tilt(self, lm_dict):
        try:
            l_sh = lm_dict.get("LEFT_SHOULDER")
            r_sh = lm_dict.get("RIGHT_SHOULDER")
            l_hip = lm_dict.get("LEFT_HIP")
            r_hip = lm_dict.get("RIGHT_HIP")
            if not (l_sh and r_sh and l_hip and r_hip):
                return None
            sh_mid = ((l_sh[0]+r_sh[0])/2.0, (l_sh[1]+r_sh[1])/2.0, (l_sh[2]+r_sh[2])/2.0)
            hip_mid = ((l_hip[0]+r_hip[0])/2.0, (l_hip[1]+r_hip[1])/2.0, (l_hip[2]+r_hip[2])/2.0)
            vx = sh_mid[0] - hip_mid[0]
            vy = sh_mid[1] - hip_mid[1]
            if vx == 0 and vy == 0:
                return 0.0
            tilt_rad = math.atan2(abs(vx), abs(vy) + 1e-8)
            return math.degrees(tilt_rad)
        except Exception:
            return None

    def update(self, raw_landmarks, t=None):
        now = t or time.time()
        lm = landmarks_to_dict(raw_landmarks)
        if not lm:
            self.state = "no_pose"
            return {"status": "no_pose", "per_side": {}}

        torso_tilt = self._torso_tilt(lm)
        triplets = self._get_triplets(lm)
        results = {"per_side": {}, "torso_tilt_deg": torso_tilt}

        sides = []
        if self.side == "both":
            sides = ["LEFT", "RIGHT"]
        elif self.side == "left":
            sides = ["LEFT"]
        else:
            sides = ["RIGHT"]

        for sd in sides:
            info = triplets.get(sd)
            if not info or not info.get("hip") or not info.get("shoulder") or not info.get("elbow") or not info.get("wrist"):
                results["per_side"][sd] = {"status": "no_pose"}
                continue

            hip = info["hip"]; sh = info["shoulder"]; el = info["elbow"]; wr = info["wrist"]

            # main abduction angle (hip - shoulder - elbow)
            ang = angle_between_3d(hip, sh, el)
            ang_s = self.smoothers[sd].update(ang)

            # elbow flexion (shoulder-elbow-wrist)
            elbow_ang = angle_between_3d(sh, el, wr)
            elbow_flexion = max(0.0, 180.0 - elbow_ang)

            # collect reasons
            reasons = []

            # form checks
            if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt}°")
            if elbow_flexion > self.max_elbow_flexion:
                reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion}°")

            # up / hold / rep logic (same pattern as shoulder_flexion)
            if ang_s >= self.target_up - self.tol:
                if self.hold_start[sd] is None:
                    self.hold_start[sd] = now
                elapsed = now - self.hold_start[sd]
                if elapsed >= self.hold_time:
                    if self.last_stage[sd] != "up_done":
                        # count rep only if form OK
                        if len(reasons) == 0:
                            self.reps[sd] += 1
                            if self.logger:
                                self.log(f"{sd}_rep_done", self.reps[sd], note=f"ang={ang_s:.1f}")
                            self.last_stage[sd] = "up_done"
                        results["per_side"][sd] = {"status": "done", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons, "reps": self.reps[sd], "hold_elapsed": elapsed}
                    else:
                        results["per_side"][sd] = {"status": "done", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons, "reps": self.reps[sd]}
                else:
                    results["per_side"][sd] = {"status": "holding", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons, "hold_elapsed": elapsed}
            elif ang_s <= self.target_down + self.tol:
                self.hold_start[sd] = None
                if self.last_stage[sd] == "up_done":
                    self.last_stage[sd] = "down"
                results["per_side"][sd] = {"status": "down", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
            else:
                self.hold_start[sd] = None
                if ang_s > self.min_moving_angle:
                    results["per_side"][sd] = {"status": "moving", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
                else:
                    results["per_side"][sd] = {"status": "idle", "angle": ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}

        return results

    def progress_along_path(self, shoulder_xy, elbow_xy, frame_wh, side="RIGHT"):
        """
        Compute a progress scalar (0..1) for visualization.
        For abduction we define a lateral->overhead path tailored per side.
        Returns (progress, start_point, end_point) where points are normalized (x,y).
        """
        w, h = frame_wh
        sx, sy = shoulder_xy
        ex, ey = elbow_xy
        # end is overhead (above shoulder)
        end = (sx, max(0.02, sy - 0.45))
        # start is lateral (out to the side). choose sign by side
        sign = 1.0 if side.upper() == "RIGHT" else -1.0
        start = (min(0.98, max(0.02, sx + sign * 0.28)), sy)

        ov = (start[0] * w, start[1] * h)
        fv = (end[0] * w, end[1] * h)
        ev = (ex * w, ey * h)
        import numpy as np
        v = np.array(fv) - np.array(ov)
        p = np.array(ev) - np.array(ov)
        denom = np.dot(v, v) + 1e-8
        t = float(np.dot(p, v) / denom)
        t_clamped = max(0.0, min(1.0, t))
        return t_clamped, start, end


# Optional: allow running this file standalone for debugging
if __name__ == "__main__":
    import cv2, mediapipe as mp
    cfg = {
        "side": "both",
        "target_angle_up": 160,
        "target_angle_down": 20,
        "tolerance_deg": 18,
        "hold_time_sec": 1.5,
        "smoothing_window": 7,
        "min_moving_angle": 8,
        "max_elbow_flexion_deg": 20,
        "max_torso_tilt_deg": 12
    }
    checker = ShoulderAbductionChecker(cfg)

    cap = cv2.VideoCapture(0)
    pose = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)
            lms = res.pose_landmarks.landmark if res.pose_landmarks else []
            out = checker.update(lms, t=time.time())
            print(out)
            cv2.imshow("Shoulder Abduction (debug)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
