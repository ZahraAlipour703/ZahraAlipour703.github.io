# # exercises/arm_raise_and_carry.py
# import time, math
# from exercises.base import BaseExerciseChecker
# from utils.angles import angle_between_3d
# from utils.smoothing import SimpleSmoother
# from utils.landmarks import landmarks_to_dict

# class ArmRaiseAndCarryChecker(BaseExerciseChecker):
#     """
#     Combined exercise:
#       - arm_raise: shoulder flexion reps with stick (up/down + hold)
#       - seated_carry: seated static carry - check elbow straightness, shoulder sway, torso tilt for duration
#       - combined: both behaviours monitored (counts reps and enforces carry constraints)
#     Config keys (under "arm_raise_and_carry"):
#       mode: "arm_raise" | "seated_carry" | "combined"
#       side: "both"|"right"|"left"
#       target_angle_up, target_angle_down, tolerance_deg, hold_time_sec, smoothing_window, min_moving_angle
#       max_elbow_flexion_deg, max_torso_tilt_deg, carry_duration_sec, carry_min_ok_fraction
#     """
#     def __init__(self, config, logger=None):
#         super().__init__("arm_raise_and_carry", config, logger)
#         c = config or {}
#         self.mode = c.get("mode", "combined")
#         self.side = c.get("side", "both").lower()
#         # arm raise params
#         self.target_up = float(c.get("target_angle_up", 160))
#         self.target_down = float(c.get("target_angle_down", 40))
#         self.tol = float(c.get("tolerance_deg", 12))
#         self.hold_time = float(c.get("hold_time_sec", 1.5))
#         self.smoother_window = int(c.get("smoothing_window", 5))
#         self.min_moving_angle = float(c.get("min_moving_angle", 8))
#         # carry / form params
#         self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 20))
#         self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18))
#         self.carry_duration = float(c.get("carry_duration_sec", 20))  # how long to hold carry
#         # fraction of time must be OK during carry (0-1)
#         self.carry_min_ok_fraction = float(c.get("carry_min_ok_fraction", 0.9))

#         # state per side
#         self.smoothers = {"LEFT": SimpleSmoother(self.smoother_window), "RIGHT": SimpleSmoother(self.smoother_window)}
#         self.hold_start = {"LEFT": None, "RIGHT": None}       # for up hold (reps)
#         self.reps = {"LEFT": 0, "RIGHT": 0}
#         self.last_stage = {"LEFT": "down", "RIGHT": "down"}

#         # carry tracking
#         self.carry_start = None
#         self.carry_ok_time = 0.0

#     def _get_triplets(self, dt):
#         """Return triplets for left/right if available (hip, shoulder, elbow, wrist) as normalized coords"""
#         pairs = {}
#         if "RIGHT_SHOULDER" in dt:
#             pairs["RIGHT"] = {
#                 "hip": dt.get("RIGHT_HIP"),
#                 "shoulder": dt.get("RIGHT_SHOULDER"),
#                 "elbow": dt.get("RIGHT_ELBOW"),
#                 "wrist": dt.get("RIGHT_WRIST"),
#             }
#         if "LEFT_SHOULDER" in dt:
#             pairs["LEFT"] = {
#                 "hip": dt.get("LEFT_HIP"),
#                 "shoulder": dt.get("LEFT_SHOULDER"),
#                 "elbow": dt.get("LEFT_ELBOW"),
#                 "wrist": dt.get("LEFT_WRIST"),
#             }
#         return pairs

#     def _torso_tilt(self, dt):
#         try:
#             l_sh = dt.get("LEFT_SHOULDER"); r_sh = dt.get("RIGHT_SHOULDER")
#             l_hip = dt.get("LEFT_HIP"); r_hip = dt.get("RIGHT_HIP")
#             if not (l_sh and r_sh and l_hip and r_hip):
#                 return None
#             sh_mid = ((l_sh[0]+r_sh[0])/2.0, (l_sh[1]+r_sh[1])/2.0)
#             hip_mid = ((l_hip[0]+r_hip[0])/2.0, (l_hip[1]+r_hip[1])/2.0)
#             vx = sh_mid[0] - hip_mid[0]
#             vy = sh_mid[1] - hip_mid[1]
#             tilt_rad = math.atan2(abs(vx), abs(vy) + 1e-8)
#             return math.degrees(tilt_rad)
#         except Exception:
#             return None

#     # def update(self, raw_landmarks, t=None):
#     #     now = t or time.time()
#     #     dt = landmarks_to_dict(raw_landmarks)
#     #     if not dt:
#     #         self.state = "no_pose"
#     #         return {"status":"no_pose", "per_side": {}, "carry": {}}
#     def update(self, raw_landmarks, t=None):
#         now = t or time.time()
#         dt = 0.0
#         if self.last_update_time is not None:
#             dt = now - self.last_update_time
#         self.last_update_time = now

#         torso_tilt = self._torso_tilt(dt)
#         triplets = self._get_triplets(dt)
#         results = {"per_side": {}, "torso_tilt_deg": torso_tilt, "carry": {}}

#         # which sides to process
#         sides = ["LEFT","RIGHT"] if self.side == "both" else (["LEFT"] if self.side == "left" else ["RIGHT"])

#         # carry mode: track time and fraction OK
#         in_carry_mode = (self.mode in ("seated_carry","combined"))

#         # if carry just started, initialize timer
#         if in_carry_mode and self.carry_start is None:
#             self.carry_start = now
#             self.carry_ok_time = 0.0

#         # loop sides
#         for sd in sides:
#             info = triplets.get(sd)
#             if not info or not info.get("hip") or not info.get("shoulder") or not info.get("elbow") or not info.get("wrist"):
#                 results["per_side"][sd] = {"status":"no_pose"}
#                 continue

#             hip = info["hip"]; sh = info["shoulder"]; el = info["elbow"]; wr = info["wrist"]

#             # shoulder flexion angle for arm-raise (hip - shoulder - elbow)
#             ang = angle_between_3d(hip, sh, el)
#             ang_s = self.smoothers[sd].update(ang)

#             # elbow flexion (shoulder-elbow-wrist), compute how much bent (0 ideal)
#             elbow_ang = angle_between_3d(sh, el, wr)
#             elbow_flexion = max(0.0, 180.0 - elbow_ang)

#             # collect reasons
#             reasons = []

#             # form checks used in carry mode: elbow straight, torso tilt
#             if elbow_flexion > self.max_elbow_flexion:
#                 reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion:.0f}°")
#             if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
#                 reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")

#             # ARM RAISE logic (if mode includes arm_raise)
#             if self.mode in ("arm_raise","combined"):
#                 # up / down detection using smoothed angle
#                 if ang_s >= self.target_up - self.tol:
#                     # candidate up position
#                     if self.hold_start[sd] is None:
#                         self.hold_start[sd] = now
#                     elapsed = now - self.hold_start[sd]
#                     if elapsed >= self.hold_time:
#                         if self.last_stage[sd] != "up_done":
#                             # count only if form OK (no major reasons)
#                             if len(reasons) == 0:
#                                 self.reps[sd] += 1
#                                 if self.logger:
#                                     self.log(f"{sd}_rep_done", self.reps[sd], note=f"angle={ang_s:.1f}")
#                                 self.last_stage[sd] = "up_done"
#                                 results["per_side"][sd] = {"status":"done", "angle":ang_s,
#                                                            "elbow_flexion": elbow_flexion, "reasons": reasons, "reps": self.reps[sd], "hold_elapsed": elapsed}
#                             else:
#                                 # reached top but form incorrect -> holding but warn
#                                 results["per_side"][sd] = {"status":"holding_bad_form", "angle":ang_s,
#                                                            "elbow_flexion": elbow_flexion, "reasons": reasons, "hold_elapsed": elapsed}
#                         else:
#                             results["per_side"][sd] = {"status":"done", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons, "reps": self.reps[sd]}
#                     else:
#                         results["per_side"][sd] = {"status":"holding", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons, "hold_elapsed": elapsed}
#                 elif ang_s <= self.target_down + self.tol:
#                     # down position (reset)
#                     self.hold_start[sd] = None
#                     if self.last_stage[sd] == "up_done":
#                         self.last_stage[sd] = "down"
#                     results["per_side"][sd] = {"status":"down", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
#                 else:
#                     # moving between up/down
#                     self.hold_start[sd] = None
#                     if ang_s > self.min_moving_angle:
#                         results["per_side"][sd] = {"status":"moving", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
#                     else:
#                         results["per_side"][sd] = {"status":"idle", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}
#             else:
#                 # not arm-raise mode: just report angles and reasons
#                 results["per_side"][sd] = {"status":"monitor", "angle":ang_s, "elbow_flexion": elbow_flexion, "reasons": reasons}

#             # CARRY logic: if in carry mode, accumulate OK time
#             if in_carry_mode:
#                 # define OK for carry at this moment: no major reasons and elbows adtost straight
#                 per_ok = (len(reasons) == 0)
#                 if per_ok:
#                     # accumulate ok time
#                     self.carry_ok_time += 1.0/30.0  # assume ~30 FPS; caller can adjust by passing dt
#                 # else we do not increase ok time

#         # if carry mode active, compute carry completion fraction
#         if in_carry_mode and self.carry_start is not None:
#             total_elapsed = now - self.carry_start
#             ok_fraction = min(1.0, self.carry_ok_time / max(1e-6, total_elapsed))
#             carry_completed = (total_elapsed >= self.carry_duration) and (ok_fraction >= self.carry_min_ok_fraction)
#             results["carry"] = {"start": self.carry_start, "elapsed": total_elapsed,
#                                 "ok_time": self.carry_ok_time, "ok_fraction": ok_fraction,
#                                 "required_duration": self.carry_duration, "completed": carry_completed}
#         else:
#             results["carry"] = {"completed": False, "elapsed": 0.0, "ok_fraction": 0.0}

#         return results

#     def progress_along_path(self, shoulder_xy, elbow_xy, frame_wh):
#         # same projection helper as previous files
#         w, h = frame_wh
#         sx, sy = shoulder_xy
#         ex, ey = elbow_xy
#         overhead = (sx, max(0.02, sy - 0.45))
#         front = (sx, min(0.98, sy + 0.25))
#         ov = (overhead[0]*w, overhead[1]*h)
#         fv = (front[0]*w, front[1]*h)
#         ev = (ex*w, ey*h)
#         import numpy as np
#         v = np.array(fv) - np.array(ov)
#         p = np.array(ev) - np.array(ov)
#         denom = np.dot(v, v) + 1e-8
#         t = float(np.dot(p, v) / denom)
#         t_clamped = max(0.0, min(1.0, t))
#         return t_clamped, overhead, front

# exercises/arm_raise_and_carry.py
import time, math
from exercises.base import BaseExerciseChecker
from utils.angles import angle_between_3d
from utils.smoothing import SimpleSmoother
from utils.landmarks import landmarks_to_dict

class ArmRaiseAndCarryChecker(BaseExerciseChecker):
    """
    Combined exercise:
      - arm_raise: shoulder flexion reps with stick (up/down + hold)
      - seated_carry: seated static carry - check elbow straightness, shoulder sway, torso tilt for duration
      - combined: both behaviours monitored (counts reps and enforces carry constraints)
    Config keys (under "arm_raise_and_carry"):
      mode: "arm_raise" | "seated_carry" | "combined"
      side: "both"|"right"|"left"
      target_angle_up, target_angle_down, tolerance_deg, hold_time_sec, smoothing_window, min_moving_angle
      max_elbow_flexion_deg, max_torso_tilt_deg, carry_duration_sec, carry_min_ok_fraction
    """
    def __init__(self, config, logger=None):
        super().__init__("arm_raise_and_carry", config, logger)
        c = config or {}
        self.mode = c.get("mode", "combined")
        self.side = c.get("side", "both").lower()
        # arm raise params
        self.target_up = float(c.get("target_angle_up", 160))
        self.target_down = float(c.get("target_angle_down", 40))
        self.tol = float(c.get("tolerance_deg", 12))
        self.hold_time = float(c.get("hold_time_sec", 1.5))
        self.smoother_window = int(c.get("smoothing_window", 5))
        self.min_moving_angle = float(c.get("min_moving_angle", 8))
        # carry / form params
        self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 20))
        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18))
        self.carry_duration = float(c.get("carry_duration_sec", 4))  # how long to hold carry
        # fraction of time must be OK during carry (0-1)
        self.carry_min_ok_fraction = float(c.get("carry_min_ok_fraction", 0.9))

        # state per side
        self.smoothers = {
            "LEFT": SimpleSmoother(self.smoother_window),
            "RIGHT": SimpleSmoother(self.smoother_window)
        }
        self.hold_start = {"LEFT": None, "RIGHT": None}       # for up hold (reps)
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "down", "RIGHT": "down"}

        # carry tracking
        self.carry_start = None
        self.carry_ok_time = 0.0

        # timing
        self.last_update_time = None

    def _get_triplets(self, dt):
        """Return triplets for left/right if available (hip, shoulder, elbow, wrist) as normalized coords"""
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

        # compute delta time (for FPS-independent timers)
        dt_time = 0.0
        if self.last_update_time is not None:
            dt_time = now - self.last_update_time
        self.last_update_time = now

        # convert landmarks to dict
        dt = landmarks_to_dict(raw_landmarks)
        if not dt:
            self.state = "no_pose"
            return {"status": "no_pose", "per_side": {}, "carry": {}}

        torso_tilt = self._torso_tilt(dt)
        triplets = self._get_triplets(dt)
        results = {"per_side": {}, "torso_tilt_deg": torso_tilt, "carry": {}}

        # which sides to process
        sides = ["LEFT","RIGHT"] if self.side == "both" else (["LEFT"] if self.side == "left" else ["RIGHT"])

        # carry mode: track time and fraction OK
        in_carry_mode = (self.mode in ("seated_carry","combined"))

        # if carry just started, initialize timer
        if in_carry_mode and self.carry_start is None:
            self.carry_start = now
            self.carry_ok_time = 0.0

        # loop sides
        for sd in sides:
            info = triplets.get(sd)
            if not info or not info.get("hip") or not info.get("shoulder") or not info.get("elbow") or not info.get("wrist"):
                results["per_side"][sd] = {"status":"no_pose"}
                continue

            hip = info["hip"]; sh = info["shoulder"]; el = info["elbow"]; wr = info["wrist"]

            # shoulder flexion angle for arm-raise (hip - shoulder - elbow)
            ang = angle_between_3d(hip, sh, el)
            ang_s = self.smoothers[sd].update(ang)

            # elbow flexion (shoulder-elbow-wrist), compute how much bent (0 ideal)
            elbow_ang = angle_between_3d(sh, el, wr)
            elbow_flexion = max(0.0, 180.0 - elbow_ang)

            # collect reasons
            reasons = []

            # form checks used in carry mode: elbow straight, torso tilt
            if elbow_flexion > self.max_elbow_flexion:
                reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion:.0f}°")
            if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")

            # ARM RAISE logic (if mode includes arm_raise)
            if self.mode in ("arm_raise","combined"):
                if ang_s >= self.target_up - self.tol:
                    if self.hold_start[sd] is None:
                        self.hold_start[sd] = now
                    elapsed = now - self.hold_start[sd]
                    if elapsed >= self.hold_time:
                        if self.last_stage[sd] != "up_done":
                            if len(reasons) == 0:
                                self.reps[sd] += 1
                                if self.logger:
                                    self.log(f"{sd}_rep_done", self.reps[sd], note=f"angle={ang_s:.1f}")
                                self.last_stage[sd] = "up_done"
                                results["per_side"][sd] = {
                                    "status":"done","angle":ang_s,"elbow_flexion": elbow_flexion,
                                    "reasons": reasons,"reps": self.reps[sd],"hold_elapsed": elapsed
                                }
                            else:
                                results["per_side"][sd] = {
                                    "status":"holding_bad_form","angle":ang_s,
                                    "elbow_flexion": elbow_flexion,"reasons": reasons,"hold_elapsed": elapsed
                                }
                        else:
                            results["per_side"][sd] = {
                                "status":"done","angle":ang_s,"elbow_flexion": elbow_flexion,
                                "reasons": reasons,"reps": self.reps[sd]
                            }
                    else:
                        results["per_side"][sd] = {
                            "status":"holding","angle":ang_s,"elbow_flexion": elbow_flexion,
                            "reasons": reasons,"hold_elapsed": elapsed
                        }
                elif ang_s <= self.target_down + self.tol:
                    self.hold_start[sd] = None
                    if self.last_stage[sd] == "up_done":
                        self.last_stage[sd] = "down"
                    results["per_side"][sd] = {
                        "status":"down","angle":ang_s,"elbow_flexion": elbow_flexion,"reasons": reasons
                    }
                else:
                    self.hold_start[sd] = None
                    if ang_s > self.min_moving_angle:
                        results["per_side"][sd] = {
                            "status":"moving","angle":ang_s,"elbow_flexion": elbow_flexion,"reasons": reasons
                        }
                    else:
                        results["per_side"][sd] = {
                            "status":"idle","angle":ang_s,"elbow_flexion": elbow_flexion,"reasons": reasons
                        }
            else:
                results["per_side"][sd] = {
                    "status":"monitor","angle":ang_s,"elbow_flexion": elbow_flexion,"reasons": reasons
                }

            # CARRY logic: if in carry mode, accumulate OK time
            if in_carry_mode:
                per_ok = (len(reasons) == 0)
                if per_ok:
                    self.carry_ok_time += dt_time  # ✅ FPS-independent accumulation

        # if carry mode active, compute carry completion fraction
        if in_carry_mode and self.carry_start is not None:
            total_elapsed = now - self.carry_start
            ok_fraction = min(1.0, self.carry_ok_time / max(1e-6, total_elapsed))
            carry_completed = (total_elapsed >= self.carry_duration) and (ok_fraction >= self.carry_min_ok_fraction)
            results["carry"] = {
                "start": self.carry_start,"elapsed": total_elapsed,"ok_time": self.carry_ok_time,
                "ok_fraction": ok_fraction,"required_duration": self.carry_duration,"completed": carry_completed
            }
        else:
            results["carry"] = {"completed": False, "elapsed": 0.0, "ok_fraction": 0.0}

        return results

    def progress_along_path(self, shoulder_xy, elbow_xy, frame_wh):
        w, h = frame_wh
        sx, sy = shoulder_xy
        ex, ey = elbow_xy
        overhead = (sx, max(0.02, sy - 0.45))
        front = (sx, min(0.98, sy + 0.25))
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
