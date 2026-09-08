
# import cv2
# import numpy as np
# import math
# import time


# class WallCalfStretchChecker:
#     """
#     WallCalfStretchChecker

#     Usage:
#         checker = WallCalfStretchChecker(config, logger=csv_writer)
#         img, res = checker.update(img, lm_dict, (frame_width, frame_height))

#     res = {"reps": int, "stage": "relaxed"/"stretched"/"unknown", "feedback": [...]}
#     """

#     def __init__(self, config=None, logger=None):
#         c = config or {}
#         self.side = c.get("side", "both").lower()  # "left", "right", or "both"

#         # thresholds (degrees) — tunable in config.json
#         self.ankle_stretch_thresh = float(c.get("ankle_stretch_thresh_deg", 170))
#         self.ankle_relax_thresh = float(c.get("ankle_relax_thresh_deg", 175))
#         self.wrist_stretch_thresh = float(c.get("wrist_stretch_thresh_deg", 150))
#         self.wrist_relax_thresh = float(c.get("wrist_relax_thresh_deg", 170))
#         self.arm_straight_thresh = float(c.get("arm_straight_thresh_deg", 160))  # shoulder-elbow-wrist

#         # hysteresis/tolerance
#         self.tol = float(c.get("tolerance_deg", 6))

#         # per-side state
#         self.reps = {"LEFT": 0, "RIGHT": 0}
#         self.last_stage = {"LEFT": "relaxed", "RIGHT": "relaxed"}

#         self.logger = logger

#     # -------------------------
#     # helpers
#     # -------------------------
#     def _to_pixel(self, pt, frame_size):
#         if pt is None:
#             return None
#         W, H = frame_size
#         x, y = float(pt[0]), float(pt[1])
#         # heuristic: normalized coords (<=1.5)
#         if x <= 1.5 and y <= 1.5:
#             return (x * W, y * H)
#         return (x, y)

#     def _get_candidate_keys(self, side, short_name):
#         s_up = side.upper()
#         s_lo = side.lower()
#         sn_up = short_name.upper()
#         sn_lo = short_name.lower()
#         variants = [
#             f"{s_up}_{sn_up}",
#             f"{s_lo}_{sn_lo}",
#             f"{s_lo}{sn_lo}",
#             f"{sn_up}",
#             f"{sn_lo}",
#         ]
#         if short_name == "foot_index":
#             variants += [
#                 f"{s_up}_FOOT_INDEX",
#                 f"{s_lo}_foot_index",
#                 f"{s_up}_FOOTINDEX",
#                 f"{s_lo}_footindex",
#             ]
#         return variants

#     def _lookup_point(self, lm_dict, side, name, frame_size):
#         for k in self._get_candidate_keys(side, name):
#             if k in lm_dict:
#                 return self._to_pixel(lm_dict[k], frame_size)
#         return None

#     def _angle_2d(self, a, b, c):
#         """Angle at b formed by a-b-c using 2D coordinates (pixels)."""
#         if not (a and b and c):
#             return None
#         a = np.array(a, dtype=float)
#         b = np.array(b, dtype=float)
#         c = np.array(c, dtype=float)
#         v1 = a - b
#         v2 = c - b
#         denom = np.linalg.norm(v1) * np.linalg.norm(v2)
#         if denom == 0:
#             return None
#         cosang = np.dot(v1, v2) / denom
#         cosang = float(np.clip(cosang, -1.0, 1.0))
#         ang = math.degrees(math.acos(cosang))
#         return ang if ang <= 180.0 else 360.0 - ang

#     # -------------------------
#     # per-side processing
#     # -------------------------
#     def _process_side(self, img, side, frame_size, lm_dict, idx):
#         SD = side.upper()

#         # joints
#         knee = self._lookup_point(lm_dict, side, "knee", frame_size)
#         ankle = self._lookup_point(lm_dict, side, "ankle", frame_size)
#         foot_index = self._lookup_point(lm_dict, side, "foot_index", frame_size)
#         heel = self._lookup_point(lm_dict, side, "heel", frame_size)

#         shoulder = self._lookup_point(lm_dict, side, "shoulder", frame_size)
#         elbow = self._lookup_point(lm_dict, side, "elbow", frame_size)
#         wrist = self._lookup_point(lm_dict, side, "wrist", frame_size)
#         hand_index = self._lookup_point(lm_dict, side, "index", frame_size)

#         reasons = []
#         ankle_angle = wrist_angle = arm_angle = None
#         status = self.last_stage[SD]

#         # ankle dorsiflexion angle (knee-ankle-foot_index)
#         if knee and ankle and foot_index:
#             ankle_angle = self._angle_2d(knee, ankle, foot_index)

#         # wrist extension (elbow-wrist-hand_index)
#         if elbow and wrist and hand_index:
#             wrist_angle = self._angle_2d(elbow, wrist, hand_index)

#         # arm straightness (shoulder-elbow-wrist)
#         if shoulder and elbow and wrist:
#             arm_angle = self._angle_2d(shoulder, elbow, wrist)

#         # --- state machine with hysteresis ---
#         if ankle_angle is not None:
#             # enter stretch: ankle dorsiflexion + (wrist extended OR straight arm)
#             enter_cond = (
#                 ankle_angle <= (self.ankle_stretch_thresh + self.tol)
#                 and (
#                     wrist_angle is None
#                     or wrist_angle <= (self.wrist_stretch_thresh + self.tol)
#                     or (arm_angle is not None and arm_angle >= self.arm_straight_thresh)
#                 )
#                 and self.last_stage[SD] == "relaxed"
#             )

#             # return upright: ankle relax + (wrist relaxed OR straight arm)
#             return_cond = (
#                 ankle_angle >= (self.ankle_relax_thresh - self.tol)
#                 and (
#                     wrist_angle is None
#                     or wrist_angle >= (self.wrist_relax_thresh - self.tol)
#                     or (arm_angle is not None and arm_angle >= self.arm_straight_thresh)
#                 )
#                 and self.last_stage[SD] == "stretched"
#             )

#             if enter_cond:
#                 self.last_stage[SD] = "stretched"
#                 status = "stretched"

#             elif return_cond:
#                 self.reps[SD] += 1
#                 if self.logger:
#                     try:
#                         self.logger.writerow(
#                             [
#                                 time.time(),
#                                 "wall_calf_stretch",
#                                 f"{SD}_rep_done",
#                                 self.reps[SD],
#                                 f"ankle={ankle_angle:.1f}",
#                                 f"wrist={wrist_angle:.1f}" if wrist_angle is not None else "wrist=None",
#                                 f"arm={arm_angle:.1f}" if arm_angle is not None else "arm=None",
#                             ]
#                         )
#                     except Exception:
#                         pass
#                 self.last_stage[SD] = "relaxed"
#                 status = "relaxed"

#         # annotate joints
#         for pt in (knee, ankle, foot_index, heel, shoulder, elbow, wrist, hand_index):
#             if pt:
#                 cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (30, 130, 255), -1)
#                 cv2.circle(img, (int(pt[0]), int(pt[1])), 8, (0, 0, 0), 2)

#         # draw small skeleton lines
#         def L(a, b):
#             if a and b:
#                 cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (200, 220, 255), 3)

#         L(knee, ankle)
#         L(ankle, foot_index)
#         L(shoulder, elbow)
#         L(elbow, wrist)

#         # HUD for this side
#         self._draw_hud(img, SD, ankle_angle, wrist_angle, arm_angle, self.reps[SD], status, reasons, idx)

#     # -------------------------
#     # HUD draw
#     # -------------------------
#     def _draw_hud(self, img, side, ankle_angle, wrist_angle, arm_angle, reps, status, reasons, idx):
#         hud_x = 12
#         hud_y = 80 + idx * 130
#         rect_w, rect_h = 340, 130
#         cv2.rectangle(
#             img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0, 0, 0, 80), -1
#         )

#         cv2.putText(img, f"{side} SIDE", (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
#         ankle_txt = f"Ankle: {int(ankle_angle)}°" if ankle_angle is not None else "Ankle: -"
#         wrist_txt = f"Wrist: {int(wrist_angle)}°" if wrist_angle is not None else "Wrist: -"
#         arm_txt = f"Arm: {int(arm_angle)}°" if arm_angle is not None else "Arm: -"
#         rep_txt = f"Reps: {reps}  Stage: {status}"

#         cv2.putText(img, ankle_txt, (hud_x, hud_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 220, 200), 2, cv2.LINE_AA)
#         cv2.putText(img, wrist_txt, (hud_x, hud_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 220, 255), 2, cv2.LINE_AA)
#         cv2.putText(img, arm_txt, (hud_x, hud_y + 76), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 200, 200), 2, cv2.LINE_AA)
#         cv2.putText(img, rep_txt, (hud_x, hud_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

#         wy = hud_y + 120
#         for r in reasons:
#             cv2.putText(img, f"⚠ {r}", (hud_x, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
#             wy += 18

#     # -------------------------
#     # public update (unified interface)
#     # -------------------------
#     def update(self, img, lm_dict, frame_size):
#         sides = ["left", "right"] if self.side == "both" else [self.side]

#         feedback_msgs = []
#         current_stage = "unknown"

#         for idx, sd in enumerate(sides):
#             self._process_side(img, sd, frame_size, lm_dict, idx)
#             stage = self.last_stage.get(sd.upper(), "relaxed")
#             if current_stage == "unknown":
#                 current_stage = stage

#         total_reps = self.reps["LEFT"] + self.reps["RIGHT"]

#         # global overlay
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
#         cv2.putText(img, f"Total reps: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

#         return img, {"reps": total_reps, "stage": current_stage, "feedback": feedback_msgs}

import cv2
import numpy as np
import math
import time


class WallCalfStretchChecker:
    """
    Wall Standing Calf Stretch posture & rep monitor.
    """

    def __init__(self, config=None, logger=None):
        c = config or {}
        self.side = c.get("side", "both").lower()

        # Doctor-defined thresholds
        self.knee_target = float(c.get("knee_angle_target_deg", 175))
        self.hip_target = float(c.get("hip_angle_target_deg", 170))
        self.wrist_flat_angle = float(c.get("wrist_flat_deg", 90))
        self.elbow_straight_thresh = float(c.get("elbow_straight_deg", 160))
        self.lumbar_max_tilt = float(c.get("lumbar_max_tilt_deg", 10))
        self.head_dev_thresh = float(c.get("head_dev_deg", 15))

        # Stretch vs relax thresholds
        self.ankle_stretch_thresh = float(c.get("ankle_stretch_deg", 170))
        self.ankle_relax_thresh = float(c.get("ankle_relax_deg", 175))
        self.tol = float(c.get("tolerance_deg", 6))

        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "relaxed", "RIGHT": "relaxed"}
        self.logger = logger

    # ----------------- geometry helpers -----------------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        if x <= 1.5 and y <= 1.5:
            return (x * W, y * H)
        return (x, y)

    def _get_keys(self, side, name):
        sU, sL = side.upper(), side.lower()
        nU, nL = name.upper(), name.lower()
        return [f"{sU}_{nU}", f"{sL}_{nL}", f"{sU}{nU}", f"{sL}{nL}", nU, nL]

    def _p(self, lm, side, name, fs):
        for k in self._get_keys(side, name):
            if k in lm:
                return self._to_pixel(lm[k], fs)
        return None

    def _angle(self, a, b, c):
        if not (a and b and c):
            return None
        a, b, c = np.array(a), np.array(b), np.array(c)
        v1, v2 = a - b, c - b
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return None
        cosang = np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)
        return math.degrees(math.acos(cosang))

    def _torso_tilt(self, lsh, rsh, lhip, rhip):
        if not (lsh and rsh and lhip and rhip):
            return None
        sm = ((lsh[0] + rsh[0]) / 2, (lsh[1] + rsh[1]) / 2)
        hm = ((lhip[0] + rhip[0]) / 2, (lhip[1] + rhip[1]) / 2)
        dx, dy = abs(sm[0] - hm[0]), abs(sm[1] - hm[1]) + 1e-6
        return math.degrees(math.atan2(dx, dy))

    def _head_tilt(self, nose, neck, shoulders_mid):
        if not (nose and neck and shoulders_mid):
            return None
        v1 = np.array(nose) - np.array(neck)
        v2 = np.array(shoulders_mid) - np.array(neck)
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return None
        cosang = np.clip(np.dot(v1, v2) / denom, -1.0, 1.0)
        return math.degrees(math.acos(cosang))

    # ---------------------------------------------------
    def _process_side(self, img, side, fs, lm, idx):
        SD = side.upper()
        feedback = []

        # --- joints ---
        hip = self._p(lm, side, "hip", fs)
        knee = self._p(lm, side, "knee", fs)
        ankle = self._p(lm, side, "ankle", fs)
        foot = self._p(lm, side, "foot_index", fs)

        shoulder = self._p(lm, side, "shoulder", fs)
        elbow = self._p(lm, side, "elbow", fs)
        wrist = self._p(lm, side, "wrist", fs)
        finger = self._p(lm, side, "index", fs)

        # body-center points
        lsh, rsh = self._p(lm, "left", "shoulder", fs), self._p(lm, "right", "shoulder", fs)
        lhip, rhip = self._p(lm, "left", "hip", fs), self._p(lm, "right", "hip", fs)
        nose, neck = self._p(lm, "mid", "nose", fs), self._p(lm, "mid", "neck", fs)

        # --- compute angles ---
        knee_ang = self._angle(hip, knee, ankle)
        hip_ang = self._angle(shoulder, hip, knee)
        wrist_ang = self._angle(elbow, wrist, finger)
        elbow_ang = self._angle(shoulder, elbow, wrist)

        torso_tilt = self._torso_tilt(lsh, rsh, lhip, rhip)
        shoulders_mid = ((lsh[0] + rsh[0]) / 2, (lsh[1] + rsh[1]) / 2) if (lsh and rsh) else None
        head_dev = self._head_tilt(nose, neck, shoulders_mid)

        # --- check posture rules ---
        if wrist_ang and abs(wrist_ang - self.wrist_flat_angle) > 20:
            feedback.append("Wrist not flat")
        if elbow_ang and elbow_ang < self.elbow_straight_thresh:
            feedback.append("Elbows not straight")
        if torso_tilt and torso_tilt > self.lumbar_max_tilt:
            feedback.append("Bending lumbar spine")
        if head_dev and head_dev > self.head_dev_thresh:
            feedback.append("Head not neutral")
        if hip_ang and hip_ang < self.hip_target - 10:
            feedback.append("Hip angle too small")
        if knee_ang and knee_ang < self.knee_target - 10:
            feedback.append("Knee angle too small")

        # --- rep logic (stretch → relax) ---
        stage = self.last_stage[SD]
        if ankle and knee and foot:
            ankle_ang = self._angle(knee, ankle, foot)
        else:
            ankle_ang = None

        if ankle_ang:
            if ankle_ang <= (self.ankle_stretch_thresh + self.tol) and stage == "relaxed":
                self.last_stage[SD] = "stretched"
            elif ankle_ang >= (self.ankle_relax_thresh - self.tol) and stage == "stretched":
                self.reps[SD] += 1
                self.last_stage[SD] = "relaxed"
                if self.logger:
                    self.logger.writerow([time.time(), "wall_calf_stretch", f"{SD}_rep", self.reps[SD]])

        # --- draw ---
        # for pt in [hip, knee, ankle, shoulder, elbow, wrist, finger]:
        #     if pt:
        #         cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (255, 240, 150), -1)

        # def L(a, b):
        #     if a and b:
        #         cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (180, 220, 255), 2)

        # L(shoulder, elbow)
        # L(elbow, wrist)
        # L(hip, knee)
        # L(knee, ankle)

        # show angles nearby
        def txt(p, label, ang):
            if p and ang is not None:
                cv2.putText(img, f"{label}:{int(ang)}°", (int(p[0]) + 8, int(p[1]) - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        txt(knee, "K", knee_ang)
        txt(hip, "H", hip_ang)
        txt(elbow, "E", elbow_ang)
        txt(wrist, "W", wrist_ang)

        # side HUD
        x, y0 = 15, 80 + idx * 120
        cv2.putText(img, f"{SD} side  Reps:{self.reps[SD]}  Stage:{self.last_stage[SD]}",
                    (x, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        for i, f in enumerate(feedback):
            cv2.putText(img, f"⚠ {f}", (x, y0 + 25 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        if not feedback:
            cv2.putText(img, "✅ Good posture", (x, y0 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

    # ---------------------------------------------------
    def update(self, img, lm_dict, frame_size):
        sides = ["left", "right"] if self.side == "both" else [self.side]
        for i, s in enumerate(sides):
            self._process_side(img, s, frame_size, lm_dict, i)

        total = self.reps["LEFT"] + self.reps["RIGHT"]
        cv2.putText(img, f"Total Reps:{total}", (12, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        return img, {"reps": total, "stage": "active"}
