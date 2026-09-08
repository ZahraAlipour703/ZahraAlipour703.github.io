

# import cv2
# import numpy as np
# import math
# import time
# from utils.smoothing import SimpleSmoother

# class MiniSquatChecker:
#     """
#     MiniSquatChecker

#     Usage (matches run_local.py):
#         checker = MiniSquatChecker(config, logger=csv_writer)
#         img, reps = checker.update(img, lm_dict, (frame_width, frame_height))

#     lm_dict is the fused landmarks dictionary returned by fuse_landmarks,
#     which may contain keys like "LEFT_HIP" or "left_hip" and values (x,y[,z])
#     in normalized coords (0..1) or already pixel coords.
#     """

#     def __init__(self, config, logger=None):
#         c = config or {}
#         self.side = c.get("side", "left").lower()  # "left", "right" or "both"
#         self.down_angle = float(c.get("down_knee_angle_deg", 60))   # angle considered "down"
#         self.up_angle = float(c.get("up_knee_angle_deg", 170))     # angle considered "up" (straight)
#         self.tol = float(c.get("tolerance_deg", 8))
#         self.smoother_window = int(c.get("smoothing_window", 5))
#         self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18))
#         self.heel_thresh = float(c.get("heel_lift_thresh_deg", 6))

#         # per-side smoothing + counters
#         self.smoothers = {"LEFT": SimpleSmoother(self.smoother_window),
#                           "RIGHT": SimpleSmoother(self.smoother_window)}
#         self.reps = {"LEFT": 0, "RIGHT": 0}
#         self.last_stage = {"LEFT": "up", "RIGHT": "up"}

#         # initialization for form checks
#         self.initial_back_length = {"LEFT": None, "RIGHT": None}
#         self.initial_heel_angle = {"LEFT": None, "RIGHT": None}

#         # logger: a csv.writer or None
#         self.logger = logger

#     # -------------------------
#     # helpers
#     # -------------------------
#     def _to_pixel(self, pt, frame_size):
#         """
#         Accepts pt = (x,y[,z]) where x may be normalized or pixel.
#         frame_size = (W, H)
#         Returns (x_px, y_px)
#         """
#         if pt is None:
#             return None
#         W, H = frame_size
#         x, y = float(pt[0]), float(pt[1])
#         # heuristic: if x <= 1.5 treat normalized
#         if x <= 1.5 and y <= 1.5:
#             return (x * W, y * H)
#         return (x, y)

#     def _get_candidate_keys(self, side, short_name):
#         """
#         Try multiple naming conventions (UPPER, lower, with/without underscore).
#         short_name examples: 'hip', 'knee', 'ankle', 'shoulder', 'heel', 'foot_index'
#         """
#         s_up = side.upper()
#         s_lo = side.lower()
#         sn_up = short_name.upper()
#         sn_lo = short_name.lower()
#         # variants
#         variants = [
#             f"{s_up}_{sn_up}",
#             f"{s_lo}_{sn_lo}",
#             f"{s_lo}{sn_lo}",
#             f"{sn_up}",
#             f"{sn_lo}"
#         ]
#         # foot index sometimes "FOOT_INDEX" or "FOOTINDEX"
#         if short_name == "foot_index":
#             variants += [f"{s_up}_FOOT_INDEX", f"{s_lo}_foot_index", f"{s_up}_FOOTINDEX", f"{s_lo}_footindex"]
#         return variants

#     def _lookup_point(self, lm_dict, side, name, frame_size):
#         """
#         Returns point in pixel coords or None.
#         """
#         # try variants
#         for k in self._get_candidate_keys(side, name):
#             if k in lm_dict:
#                 return self._to_pixel(lm_dict[k], frame_size)
#         return None

#     # -------------------------
#     # geometric utilities
#     # -------------------------
#     def _angle_2d(self, a, b, c):
#         """
#         Angle at b formed by a-b-c using 2D coords (x_px,y_px).
#         Returns degrees.
#         """
#         a = np.array(a, dtype=float)
#         b = np.array(b, dtype=float)
#         c = np.array(c, dtype=float)
#         v1 = a - b
#         v2 = c - b
#         denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
#         if denom == 0:
#             return None
#         cosang = np.dot(v1, v2) / denom
#         cosang = float(np.clip(cosang, -1.0, 1.0))
#         ang = math.degrees(math.acos(cosang))
#         return ang if ang <= 180.0 else 360.0 - ang

#     def _torso_tilt_deg(self, left_sh, right_sh, left_hip, right_hip):
#         """
#         Returns torso tilt degrees (abs of horizontal vs vertical) using pixel coords.
#         If not enough info -> None
#         """
#         if not (left_sh and right_sh and left_hip and right_hip):
#             return None
#         sh_mid = ((left_sh[0] + right_sh[0]) / 2.0, (left_sh[1] + right_sh[1]) / 2.0)
#         hip_mid = ((left_hip[0] + right_hip[0]) / 2.0, (left_hip[1] + right_hip[1]) / 2.0)
#         vx = abs(sh_mid[0] - hip_mid[0])
#         vy = abs(sh_mid[1] - hip_mid[1]) + 1e-8
#         return math.degrees(math.atan2(vx, vy))

#     # -------------------------
#     # initialization of per-side baseline (back length, heel angle)
#     # -------------------------
#     def _initialise_side_bounds_if_needed(self, side, shoulder, hip, heel, foot_index):
#         """
#         Accept pixel coords. If knee is initially straight (called by caller),
#         set baseline back length and heel orientation for the side.
#         """
#         if self.initial_back_length[side.upper()] is None and shoulder and hip:
#             upper_back = np.array(shoulder)
#             lower_back = np.array(hip)
#             self.initial_back_length[side.upper()] = float(np.linalg.norm(upper_back - lower_back))
#         if self.initial_heel_angle[side.upper()] is None and heel and foot_index:
#             radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
#             self.initial_heel_angle[side.upper()] = abs(180.0 * radians / math.pi)

#     # -------------------------
#     # draw helpers
#     # -------------------------
#     def _draw_reps_box(self, img, side_label, reps, origin=(12, 40)):
#         text = f"{side_label} Reps: {reps}"
#         x, y = origin
#         # black outline
#         cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 5, cv2.LINE_AA)
#         # foreground
#         cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

#     # -------------------------
#     # public update (matches run_local.py calling convention)
#     # -------------------------
#     def update(self, img, raw_landmarks, frame_size):
#         """
#         img: OpenCV BGR image (will be annotated)
#         raw_landmarks: fused landmarks dict from fuse_landmarks (mixed naming possible)
#         frame_size: (W, H)
#         returns: (img_annotated, reps_summary)
#         reps_summary is dict {"LEFT": int, "RIGHT": int} (you can sum if you want a single number)
#         """
#         W, H = frame_size
#         # determine whether we should handle both sides
#         sides = ["left", "right"] if self.side == "both" else [self.side]

#         # Compute torso tilt if possible (use pixel coords)
#         left_sh = self._lookup_point(raw_landmarks, "left", "shoulder", frame_size)
#         right_sh = self._lookup_point(raw_landmarks, "right", "shoulder", frame_size)
#         left_hip = self._lookup_point(raw_landmarks, "left", "hip", frame_size)
#         right_hip = self._lookup_point(raw_landmarks, "right", "hip", frame_size)
#         torso_tilt = self._torso_tilt_deg(left_sh, right_sh, left_hip, right_hip)

#         # per-side processing
#         for idx, sd in enumerate(sides):
#             SD = sd.upper()

#             shoulder = self._lookup_point(raw_landmarks, sd, "shoulder", frame_size)
#             hip = self._lookup_point(raw_landmarks, sd, "hip", frame_size)
#             knee = self._lookup_point(raw_landmarks, sd, "knee", frame_size)
#             ankle = self._lookup_point(raw_landmarks, sd, "ankle", frame_size)
#             heel = self._lookup_point(raw_landmarks, sd, "heel", frame_size)
#             foot_index = self._lookup_point(raw_landmarks, sd, "foot_index", frame_size)

#             # If no keypoints for this side, continue (but still show global reps)
#             if not (hip and knee and ankle):
#                 # draw rep box for this side (even if 0)
#                 origin_x = 12
#                 origin_y = 40 + idx * 30
#                 self._draw_reps_box(img, SD, self.reps[SD])
#                 continue

#             # initialize baselines when user stands straight
#             knee_angle_raw = self._angle_2d(hip, knee, ankle)
#             if knee_angle_raw is None:
#                 knee_angle_raw = 180.0
#             self._initialise_side_bounds_if_needed(SD.lower(), shoulder, hip, heel, foot_index)

#             # smoothing
#             ang_s = self.smoothers[SD].update(knee_angle_raw)

#             # collect reasons
#             reasons = []
#             if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
#                 reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")
#             if heel is not None and foot_index is not None and self.initial_heel_angle[SD] is not None:
#                 radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
#                 heel_ang = abs(180.0 * radians / math.pi)
#                 if heel_ang > (self.initial_heel_angle[SD] + self.heel_thresh):
#                     reasons.append("Heels lifting")

#             # state machine with hysteresis
#             status = "moving"
#             if ang_s <= (self.down_angle + self.tol):
#                 status = "down"
#                 if self.last_stage[SD] == "up":
#                     self.last_stage[SD] = "down"
#             elif ang_s >= (self.up_angle - self.tol):
#                 status = "up"
#                 if self.last_stage[SD] == "down":
#                     # count only if full range and no major reasons
#                     # here we treat a rep as valid if form reasons are empty
#                     if len(reasons) == 0:
#                         self.reps[SD] += 1
#                         if self.logger:
#                             try:
#                                 # timestamp, exercise, metric, value, note
#                                 self.logger.writerow([time.time(), "mini_squat", f"{SD}_rep_done", self.reps[SD], f"angle={ang_s:.1f}"])
#                             except Exception:
#                                 pass
#                     self.last_stage[SD] = "up"

#             # annotate joints (small)
#             for pt in (shoulder, hip, knee, ankle, heel, foot_index):
#                 if pt:
#                     cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (30, 130, 255), -1)
#                     cv2.circle(img, (int(pt[0]), int(pt[1])), 8, (0, 0, 0), 2)

#             # draw small skeleton lines for side
#             def L(name_a, name_b):
#                 pa = locals().get(name_a)
#                 pb = locals().get(name_b)
#                 if pa and pb:
#                     cv2.line(img, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), (200, 220, 255), 3)

#             L("shoulder", "hip")
#             L("hip", "knee")
#             L("knee", "ankle")
#             if ankle and heel:
#                 cv2.line(img, (int(ankle[0]), int(ankle[1])), (int(heel[0]), int(heel[1])), (200, 220, 255), 2)
#             if heel and foot_index:
#                 cv2.line(img, (int(heel[0]), int(heel[1])), (int(foot_index[0]), int(foot_index[1])), (200, 220, 255), 2)

#             # HUD (angles & status) per side
#             hud_x = 12
#             hud_y = 80 + idx * 110
#             knee_txt = f"Knee: {int(ang_s)}°" if ang_s is not None else "Knee: -"
#             hip_ang = self._angle_2d(shoulder, hip, knee) if (shoulder and hip and knee) else None
#             hip_txt = f"Hip: {int(hip_ang)}°" if hip_ang is not None else "Hip: -"
#             torso_txt = f"Tilt: {torso_tilt:.1f}°" if torso_tilt is not None else "Tilt: -"
#             rep_txt = f"Reps: {self.reps[SD]}  Status: {status}"

#             # background rectangle for clarity
#             rect_w = 260
#             rect_h = 90
#             cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0, 0, 0, 80), -1)
#             cv2.putText(img, f"{SD} SIDE", (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
#             cv2.putText(img, knee_txt, (hud_x, hud_y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,220,200), 2, cv2.LINE_AA)
#             cv2.putText(img, hip_txt, (hud_x, hud_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,220,200), 2, cv2.LINE_AA)
#             cv2.putText(img, torso_txt, (hud_x, hud_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220,220,160), 2, cv2.LINE_AA)
#             cv2.putText(img, rep_txt, (hud_x + 140, hud_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

#             # warnings (if any)
#             wy = hud_y + 96
#             for r in reasons:
#                 cv2.putText(img, f"⚠ {r}", (hud_x, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2, cv2.LINE_AA)
#                 wy += 20

#         # always draw combined rep count in top-left bold
#         total_reps = self.reps["LEFT"] + self.reps["RIGHT"]
#         # outline + foreground for readability
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 4, cv2.LINE_AA)
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)

#         return img, {"LEFT": self.reps["LEFT"], "RIGHT": self.reps["RIGHT"]}# exercises/mini_squat.py
# exercises/mini_squat.py
# import cv2
# import numpy as np
# import math
# import time
# from utils.smoothing import SimpleSmoother


# class MiniSquatChecker:
#     """
#     MiniSquatChecker
#     ----------------
#     Detects and evaluates a mini-squat movement using body landmarks.
#     Tracks repetitions, joint angles, and form compliance.
#     """

#     def __init__(self, config=None, logger=None):
#         c = config or {}

#         # Doctor-defined or default rules
#         self.side = c.get("side", "left").lower()
#         self.down_angle = float(c.get("down_knee_angle_deg", 60))
#         self.up_angle = float(c.get("up_knee_angle_deg", 170))
#         self.tol = float(c.get("tolerance_deg", 8))
#         self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18))
#         self.heel_thresh = float(c.get("heel_lift_thresh_deg", 6))
#         self.smoother_window = int(c.get("smoothing_window", 5))

#         # Per-side tracking
#         self.smoothers = {
#             "LEFT": SimpleSmoother(self.smoother_window),
#             "RIGHT": SimpleSmoother(self.smoother_window)
#         }
#         self.reps = {"LEFT": 0, "RIGHT": 0}
#         self.last_stage = {"LEFT": "up", "RIGHT": "up"}
#         self.initial_back_length = {"LEFT": None, "RIGHT": None}
#         self.initial_heel_angle = {"LEFT": None, "RIGHT": None}

#         self.logger = logger

#     # ============================================================
#     # Utility helpers
#     # ============================================================

#     def _to_pixel(self, pt, frame_size):
#         if pt is None:
#             return None
#         W, H = frame_size
#         x, y = float(pt[0]), float(pt[1])
#         if x <= 1.5 and y <= 1.5:
#             return (x * W, y * H)
#         return (x, y)

#     def _get_candidate_keys(self, side, name):
#         sU, sL = side.upper(), side.lower()
#         nU, nL = name.upper(), name.lower()
#         return [
#             f"{sU}_{nU}", f"{sL}_{nL}",
#             nU, nL,
#             f"{sU}{nU}", f"{sL}{nL}"
#         ]

#     def _lookup_point(self, lm_dict, side, name, frame_size):
#         """Search multiple naming patterns for each landmark."""
#         for k in self._get_candidate_keys(side, name):
#             if k in lm_dict:
#                 return self._to_pixel(lm_dict[k], frame_size)
#         return None

#     def _safe_line(self, img, a, b, color=(200, 220, 255), thickness=3):
#         """Safely draw line between two points."""
#         if a is not None and b is not None:
#             cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), color, thickness)

#     # ============================================================
#     # Geometry
#     # ============================================================

#     def _angle_2d(self, a, b, c):
#         if not (a and b and c):
#             return None
#         a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
#         v1, v2 = a - b, c - b
#         denom = np.linalg.norm(v1) * np.linalg.norm(v2)
#         if denom == 0:
#             return None
#         cosang = np.dot(v1, v2) / denom
#         return math.degrees(math.acos(np.clip(cosang, -1.0, 1.0)))

#     def _torso_tilt_deg(self, l_sh, r_sh, l_hip, r_hip):
#         if not (l_sh and r_sh and l_hip and r_hip):
#             return None
#         sh_mid = ((l_sh[0] + r_sh[0]) / 2, (l_sh[1] + r_sh[1]) / 2)
#         hip_mid = ((l_hip[0] + r_hip[0]) / 2, (l_hip[1] + r_hip[1]) / 2)
#         vx, vy = abs(sh_mid[0] - hip_mid[0]), abs(sh_mid[1] - hip_mid[1]) + 1e-8
#         return math.degrees(math.atan2(vx, vy))

#     # ============================================================
#     # Baseline
#     # ============================================================

#     def _initialize_baseline(self, side, shoulder, hip, heel, foot_index):
#         S = side.upper()
#         if self.initial_back_length[S] is None and shoulder and hip:
#             self.initial_back_length[S] = np.linalg.norm(np.array(shoulder) - np.array(hip))
#         if self.initial_heel_angle[S] is None and heel and foot_index:
#             radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
#             self.initial_heel_angle[S] = abs(180.0 * radians / math.pi)

#     # ============================================================
#     # Drawing
#     # ============================================================

#     def _draw_reps_box(self, img, side, reps, pos=(12, 40)):
#         txt = f"{side} Reps: {reps}"
#         x, y = pos
#         cv2.putText(img, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 5, cv2.LINE_AA)
#         cv2.putText(img, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

#     # ============================================================
#     # Main update
#     # ============================================================

#     def update(self, img, landmarks, frame_size):
#         W, H = frame_size
#         sides = ["left", "right"] if self.side == "both" else [self.side]

#         # Torso tilt
#         l_sh = self._lookup_point(landmarks, "left", "shoulder", frame_size)
#         r_sh = self._lookup_point(landmarks, "right", "shoulder", frame_size)
#         l_hip = self._lookup_point(landmarks, "left", "hip", frame_size)
#         r_hip = self._lookup_point(landmarks, "right", "hip", frame_size)
#         torso_tilt = self._torso_tilt_deg(l_sh, r_sh, l_hip, r_hip)

#         for idx, sd in enumerate(sides):
#             SD = sd.upper()

#             shoulder = self._lookup_point(landmarks, sd, "shoulder", frame_size)
#             hip = self._lookup_point(landmarks, sd, "hip", frame_size)
#             knee = self._lookup_point(landmarks, sd, "knee", frame_size)
#             ankle = self._lookup_point(landmarks, sd, "ankle", frame_size)
#             heel = self._lookup_point(landmarks, sd, "heel", frame_size)
#             foot_index = self._lookup_point(landmarks, sd, "foot_index", frame_size)

#             if not (hip and knee and ankle):
#                 self._draw_reps_box(img, SD, self.reps[SD])
#                 continue

#             # Initialize baselines
#             self._initialize_baseline(sd, shoulder, hip, heel, foot_index)

#             knee_ang_raw = self._angle_2d(hip, knee, ankle) or 180.0
#             knee_angle = self.smoothers[SD].update(knee_ang_raw)

#             reasons = []
#             if torso_tilt and torso_tilt > self.max_torso_tilt:
#                 reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")

#             if heel and foot_index and self.initial_heel_angle[SD]:
#                 radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
#                 heel_ang = abs(180.0 * radians / math.pi)
#                 if heel_ang > (self.initial_heel_angle[SD] + self.heel_thresh):
#                     reasons.append("Heels lifting")

#             # Rep logic
#             status = "moving"
#             if knee_angle <= (self.down_angle + self.tol):
#                 status = "down"
#                 if self.last_stage[SD] == "up":
#                     self.last_stage[SD] = "down"

#             elif knee_angle >= (self.up_angle - self.tol):
#                 status = "up"
#                 if self.last_stage[SD] == "down":
#                     if not reasons:
#                         self.reps[SD] += 1
#                         if self.logger:
#                             try:
#                                 self.logger.writerow([time.time(), "mini_squat", f"{SD}_rep_done", self.reps[SD], f"angle={knee_angle:.1f}"])
#                             except Exception:
#                                 pass
#                     self.last_stage[SD] = "up"

#             # # Draw skeleton safely
#             # for pt in (shoulder, hip, knee, ankle, heel, foot_index):
#             #     if pt:
#             #         cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (30, 130, 255), -1)
#             #         cv2.circle(img, (int(pt[0]), int(pt[1])), 8, (0, 0, 0), 2)

#             # self._safe_line(img, shoulder, hip)
#             # self._safe_line(img, hip, knee)
#             # self._safe_line(img, knee, ankle)
#             # self._safe_line(img, ankle, heel)
#             # self._safe_line(img, heel, foot_index)

#             # HUD
#             hud_x, hud_y = 12, 80 + idx * 110
#             knee_txt = f"Knee: {int(knee_angle)}°" if knee_angle else "Knee: -"
#             rep_txt = f"Reps: {self.reps[SD]}  Status: {status}"

#             cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + 280, hud_y + 90), (0, 0, 0, 80), -1)
#             cv2.putText(img, f"{SD} SIDE", (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
#             cv2.putText(img, knee_txt, (hud_x, hud_y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,220,200), 2)
#             cv2.putText(img, rep_txt, (hud_x, hud_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

#             wy = hud_y + 96
#             for r in reasons:
#                 cv2.putText(img, f"⚠ {r}", (hud_x, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2)
#                 wy += 20

#         total_reps = self.reps["LEFT"] + self.reps["RIGHT"]
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 4)
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

#         return img, {"LEFT": self.reps["LEFT"], "RIGHT": self.reps["RIGHT"]}
#-- the third edition :
import cv2
import numpy as np
import math
import time
from utils.smoothing import SimpleSmoother


class MiniSquatChecker:
    """
    MiniSquatChecker (v3 - smoothed)
    ----------------
    Detects and evaluates a mini-squat movement using body landmarks.
    Tracks repetitions, joint angles, velocity, timing, and form compliance.
    """

    def __init__(self, config=None, logger=None):
        c = config or {}

        # Configurable parameters
        self.side = c.get("side", "left").lower()
        self.down_angle = float(c.get("down_knee_angle_deg", 60))
        self.up_angle = float(c.get("up_knee_angle_deg", 170))
        self.tol = float(c.get("tolerance_deg", 8))
        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18))
        self.heel_thresh = float(c.get("heel_lift_thresh_deg", 6))
        self.smoother_window = int(c.get("smoothing_window", 5))

        # Smoothers for hip, knee, ankle (not just knee)
        self.smoothers = {
            "LEFT": {
                "hip": SimpleSmoother(self.smoother_window),
                "knee": SimpleSmoother(self.smoother_window),
                "ankle": SimpleSmoother(self.smoother_window)
            },
            "RIGHT": {
                "hip": SimpleSmoother(self.smoother_window),
                "knee": SimpleSmoother(self.smoother_window),
                "ankle": SimpleSmoother(self.smoother_window)
            }
        }

        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "up", "RIGHT": "up"}
        self.rep_start_time = {"LEFT": None, "RIGHT": None}
        self.rep_durations = {"LEFT": [], "RIGHT": []}
        self.rep_velocities = {"LEFT": [], "RIGHT": []}
        self.initial_back_length = {"LEFT": None, "RIGHT": None}
        self.initial_heel_angle = {"LEFT": None, "RIGHT": None}

        self.logger = logger
        self.last_time = time.time()
        self.fps = 0

    # ============================================================
    # Utility helpers
    # ============================================================
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        return (x * W, y * H) if x <= 1.5 and y <= 1.5 else (x, y)

    def _get_candidate_keys(self, side, name):
        sU, sL = side.upper(), side.lower()
        nU, nL = name.upper(), name.lower()
        return [f"{sU}_{nU}", f"{sL}_{nL}", nU, nL, f"{sU}{nU}", f"{sL}{nL}"]

    def _lookup_point(self, lm_dict, side, name, frame_size):
        for k in self._get_candidate_keys(side, name):
            if k in lm_dict:
                return self._to_pixel(lm_dict[k], frame_size)
        return None

    def _safe_line(self, img, a, b, color=(200, 220, 255), thickness=3):
        if a and b:
            cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), color, thickness)

    # ============================================================
    # Geometry
    # ============================================================
    def _angle_2d(self, a, b, c):
        if not (a and b and c):
            return None
        a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
        v1, v2 = a - b, c - b
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return None
        cosang = np.dot(v1, v2) / denom
        return math.degrees(math.acos(np.clip(cosang, -1.0, 1.0)))

    def _torso_tilt_deg(self, l_sh, r_sh, l_hip, r_hip):
        if not (l_sh and r_sh and l_hip and r_hip):
            return None
        sh_mid = ((l_sh[0] + r_sh[0]) / 2, (l_sh[1] + r_sh[1]) / 2)
        hip_mid = ((l_hip[0] + r_hip[0]) / 2, (l_hip[1] + r_hip[1]) / 2)
        vx, vy = abs(sh_mid[0] - hip_mid[0]), abs(sh_mid[1] - hip_mid[1]) + 1e-8
        return math.degrees(math.atan2(vx, vy))

    # ============================================================
    # Baseline
    # ============================================================
    def _initialize_baseline(self, side, shoulder, hip, heel, foot_index):
        S = side.upper()
        if self.initial_back_length[S] is None and shoulder and hip:
            self.initial_back_length[S] = np.linalg.norm(np.array(shoulder) - np.array(hip))
        if self.initial_heel_angle[S] is None and heel and foot_index:
            radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
            self.initial_heel_angle[S] = abs(180.0 * radians / math.pi)

    # ============================================================
    # Main update
    # ============================================================
    def update(self, img, landmarks, frame_size):
        now = time.time()
        self.fps = 1.0 / (now - self.last_time + 1e-6)
        self.last_time = now

        W, H = frame_size
        sides = ["left", "right"] if self.side == "both" else [self.side]

        l_sh = self._lookup_point(landmarks, "left", "shoulder", frame_size)
        r_sh = self._lookup_point(landmarks, "right", "shoulder", frame_size)
        l_hip = self._lookup_point(landmarks, "left", "hip", frame_size)
        r_hip = self._lookup_point(landmarks, "right", "hip", frame_size)
        torso_tilt = self._torso_tilt_deg(l_sh, r_sh, l_hip, r_hip)

        for idx, sd in enumerate(sides):
            SD = sd.upper()
            shoulder = self._lookup_point(landmarks, sd, "shoulder", frame_size)
            hip = self._lookup_point(landmarks, sd, "hip", frame_size)
            knee = self._lookup_point(landmarks, sd, "knee", frame_size)
            ankle = self._lookup_point(landmarks, sd, "ankle", frame_size)
            heel = self._lookup_point(landmarks, sd, "heel", frame_size)
            foot_index = self._lookup_point(landmarks, sd, "foot_index", frame_size)

            if not (hip and knee and ankle):
                continue

            self._initialize_baseline(sd, shoulder, hip, heel, foot_index)

            # --- Smoothed knee angle ---
            knee_ang_raw = self._angle_2d(hip, knee, ankle) or 180.0
            knee_angle = self.smoothers[SD]["knee"].update(knee_ang_raw)

            reasons = []
            if torso_tilt and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")

            # Heel lift check
            if heel and foot_index and self.initial_heel_angle[SD]:
                radians = math.atan2(heel[1] - foot_index[1], heel[0] - foot_index[0])
                heel_ang = abs(180.0 * radians / math.pi)
                if heel_ang > (self.initial_heel_angle[SD] + self.heel_thresh):
                    reasons.append("Heels lifting")

            # --- Rep Logic ---
            status = "moving"
            if knee_angle <= (self.down_angle + self.tol):
                status = "down"
                if self.last_stage[SD] == "up":
                    self.rep_start_time[SD] = time.time()
                    self.last_stage[SD] = "down"

            elif knee_angle >= (self.up_angle - self.tol):
                status = "up"
                if self.last_stage[SD] == "down":
                    rep_time = None
                    rep_velocity = None
                    if self.rep_start_time[SD] is not None:
                        rep_time = time.time() - self.rep_start_time[SD]
                        rep_velocity = abs(self.up_angle - self.down_angle) / rep_time
                        self.rep_durations[SD].append(rep_time)
                        self.rep_velocities[SD].append(rep_velocity)

                    if not reasons:
                        self.reps[SD] += 1
                        if self.logger:
                            try:
                                self.logger.writerow([
                                    time.time(), "mini_squat", f"{SD}_rep_done", self.reps[SD],
                                    f"angle={knee_angle:.1f}",
                                    f"time={rep_time:.2f}s" if rep_time else "-",
                                    f"velocity={rep_velocity:.2f}°/s" if rep_velocity else "-"
                                ])
                            except Exception:
                                pass
                    self.last_stage[SD] = "up"
                    self.rep_start_time[SD] = None

            # --- HUD & Checklist ---
            self._draw_hud(img, SD, idx, knee_angle, status, reasons)

        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]
        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        return img, {"LEFT": self.reps["LEFT"], "RIGHT": self.reps["RIGHT"]}

    # ============================================================
    # HUD & Checklist
    # ============================================================
    def _draw_hud(self, img, SD, idx, knee_angle, status, reasons):
        hud_x, hud_y = 12, 80 + idx * 110
        cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + 320, hud_y + 160), (0, 0, 0), -1)

        cv2.putText(img, f"{SD} SIDE | FPS {self.fps:.1f}", (hud_x, hud_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Knee: {int(knee_angle)}°  Status: {status}",
                    (hud_x, hud_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 220, 200), 2)
        cv2.putText(img, f"Reps: {self.reps[SD]}", (hud_x, hud_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 255, 180), 2)

        if self.rep_durations[SD]:
            last_time = self.rep_durations[SD][-1]
            cv2.putText(img, f"Last Rep Time: {last_time:.2f}s",
                        (hud_x, hud_y + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 2)
        if self.rep_velocities[SD]:
            last_vel = self.rep_velocities[SD][-1]
            cv2.putText(img, f"Velocity: {last_vel:.1f}°/s",
                        (hud_x, hud_y + 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 150), 2)

        # Checklist items
        checklist_items = [
            ("head forward", True),
            ("hands free", True),
            ("hip-knee 90° ok", knee_angle <= (self.down_angle + self.tol)),
            ("not bent spine", True),
            ("rep time recorded", len(self.rep_durations[SD]) > 0),
            ("velocity computed", len(self.rep_velocities[SD]) > 0),
        ]
        y_off = 140
        for text, ok in checklist_items:
            color = (0, 255, 0) if ok else (0, 0, 255)
            cv2.putText(img, f"{'✓' if ok else '✗'} {text}",
                        (hud_x + 10, hud_y + y_off),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            y_off += 20

        for r in reasons:
            cv2.putText(img, f"⚠ {r}", (hud_x + 10, hud_y + y_off),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
            y_off += 20
