import cv2
import numpy as np
import time

from utils.angles import angle_between_3d
from utils.landmarks import fuse_landmarks


class KettlebellSwingsChecker:
    """
    Detect and count kettlebell swings.
    Key markers: shoulders, hips, knees, wrists.
    """

    def __init__(self, config=None, logger=None):
        c = config or {}

        self.side = c.get("side", "both").lower()

        # thresholds (degrees)
        self.hinge_thresh = float(c.get("hinge_thresh_deg", 100))  # hip hinge start (hip angle closes)
        self.swing_up_thresh = float(c.get("swing_up_thresh_deg", 60))  # arms ~horizontal
        self.swing_down_thresh = float(c.get("swing_down_thresh_deg", 120))  # arms return down

        self.tol = float(c.get("tolerance_deg", 8))

        # state
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "down", "RIGHT": "down"}

        self.logger = logger

    # ----------------------------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        if x <= 1.5 and y <= 1.5:  # normalized
            return (x * W, y * H)
        return (x, y)

    def _lookup(self, lm_dict, key, frame_size):
        if key in lm_dict:
            return self._to_pixel(lm_dict[key], frame_size)
        return None

    def _angle(self, a, b, c):
        if not (a and b and c):
            return None
        return angle_between_3d(a, b, c)

    # ----------------------------
    def _process_side(self, img, side, frame_size, lm_dict, idx):
        SD = side.upper()

        # joints
        shoulder = self._lookup(lm_dict, f"{SD}_SHOULDER", frame_size)
        hip = self._lookup(lm_dict, f"{SD}_HIP", frame_size)
        knee = self._lookup(lm_dict, f"{SD}_KNEE", frame_size)
        wrist = self._lookup(lm_dict, f"{SD}_WRIST", frame_size)

        status = self.last_stage[SD]
        hip_angle, arm_angle = None, None

        # hip hinge angle (shoulder-hip-knee)
        if shoulder and hip and knee:
            hip_angle = self._angle(shoulder, hip, knee)

        # arm swing angle (hip-shoulder-wrist)
        if hip and shoulder and wrist:
            arm_angle = self._angle(hip, shoulder, wrist)

        # state machine
        if hip_angle and arm_angle:
            if arm_angle <= self.swing_up_thresh and self.last_stage[SD] == "down":
                self.last_stage[SD] = "up"
                status = "up"

            elif arm_angle >= self.swing_down_thresh and self.last_stage[SD] == "up":
                self.reps[SD] += 1
                if self.logger:
                    try:
                        self.logger.writerow([
                            time.time(),
                            "kettlebell_swings",
                            f"{SD}_rep_done",
                            self.reps[SD],
                            f"hip={hip_angle:.1f}, arm={arm_angle:.1f}"
                        ])
                    except Exception:
                        pass
                self.last_stage[SD] = "down"
                status = "down"

        # draw joints + skeleton
        for pt in (shoulder, hip, knee, wrist):
            if pt:
                cv2.circle(img, (int(pt[0]), int(pt[1])), 6, (0, 200, 255), -1)
                cv2.circle(img, (int(pt[0]), int(pt[1])), 9, (0, 0, 0), 2)

        if shoulder and hip:
            cv2.line(img, (int(shoulder[0]), int(shoulder[1])), (int(hip[0]), int(hip[1])), (255, 200, 100), 3)
        if hip and knee:
            cv2.line(img, (int(hip[0]), int(hip[1])), (int(knee[0]), int(knee[1])), (255, 200, 100), 3)
        if shoulder and wrist:
            cv2.line(img, (int(shoulder[0]), int(shoulder[1])), (int(wrist[0]), int(wrist[1])), (255, 200, 100), 3)

        # HUD
        self._draw_hud(img, SD, hip_angle, arm_angle, self.reps[SD], status, idx)

    def _draw_hud(self, img, side, hip_angle, arm_angle, reps, status, idx):
        hud_x = 12
        hud_y = 80 + idx * 120
        rect_w, rect_h = 340, 130
        cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0, 0, 0, 80), -1)

        cv2.putText(img, f"{side} SIDE", (hud_x, hud_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        hip_txt = f"Hip hinge: {int(hip_angle)}°" if hip_angle else "Hip hinge: -"
        arm_txt = f"Arm swing: {int(arm_angle)}°" if arm_angle else "Arm swing: -"
        rep_txt = f"Reps: {reps}  Stage: {status}"

        cv2.putText(img, hip_txt, (hud_x, hud_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 220, 200), 2, cv2.LINE_AA)
        cv2.putText(img, arm_txt, (hud_x, hud_y + 54),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 220, 200), 2, cv2.LINE_AA)
        cv2.putText(img, rep_txt, (hud_x, hud_y + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # ----------------------------
    def update(self, img, lm_dict, frame_size):
        sides = ["left", "right"] if self.side == "both" else [self.side]

        current_stage = "unknown"
        for idx, sd in enumerate(sides):
            self._process_side(img, sd, frame_size, lm_dict, idx)
            stage = self.last_stage.get(sd.upper(), "down")
            if current_stage == "unknown":
                current_stage = stage

        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]

        # global overlay
        cv2.putText(img, f"Kettlebell Swings | Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, f"Kettlebell Swings | Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        return img, {"reps": total_reps, "stage": current_stage, "feedback": []}
