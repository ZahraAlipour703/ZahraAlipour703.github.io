import cv2
import numpy as np
import time

from utils.angles import angle_between_3d
from utils.landmarks import fuse_landmarks


class StraightLegRaiseChecker:
    """
    Detect and count Straight Leg Raise (SLR) exercise.
    Patient may face the camera (front) or sit sideways.
    """

    def __init__(self, config=None, logger=None):
        c = config or {}

        self.side = c.get("side", "left").lower()  # "left", "right", "both"

        # thresholds (degrees)
        # hip angle: hip-knee-ankle
        self.hip_raise_thresh = float(c.get("hip_raise_thresh_deg", 140))   # enter raise when hip angle <= this
        self.hip_relax_thresh = float(c.get("hip_relax_thresh_deg", 170))   # return when >= this

        self.tol = float(c.get("tolerance_deg", 6))

        # state
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "relaxed", "RIGHT": "relaxed"}

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

        hip = self._lookup(lm_dict, f"{SD}_HIP", frame_size)
        knee = self._lookup(lm_dict, f"{SD}_KNEE", frame_size)
        ankle = self._lookup(lm_dict, f"{SD}_ANKLE", frame_size)

        status = self.last_stage[SD]
        hip_angle = None

        # measure hip angle
        if hip and knee and ankle:
            hip_angle = self._angle(hip, knee, ankle)

        # state machine
        if hip_angle is not None:
            if hip_angle <= self.hip_raise_thresh and self.last_stage[SD] == "relaxed":
                self.last_stage[SD] = "raised"
                status = "raised"

            elif hip_angle >= self.hip_relax_thresh and self.last_stage[SD] == "raised":
                self.reps[SD] += 1
                if self.logger:
                    try:
                        self.logger.writerow([
                            time.time(),
                            "straight_leg_raise",
                            f"{SD}_rep_done",
                            self.reps[SD],
                            f"hip_angle={hip_angle:.1f}"
                        ])
                    except Exception:
                        pass
                self.last_stage[SD] = "relaxed"
                status = "relaxed"

        # draw joints + skeleton
        for pt in (hip, knee, ankle):
            if pt:
                cv2.circle(img, (int(pt[0]), int(pt[1])), 6, (0, 200, 255), -1)
                cv2.circle(img, (int(pt[0]), int(pt[1])), 9, (0, 0, 0), 2)

        if hip and knee:
            cv2.line(img, (int(hip[0]), int(hip[1])), (int(knee[0]), int(knee[1])), (255, 200, 100), 3)
        if knee and ankle:
            cv2.line(img, (int(knee[0]), int(knee[1])), (int(ankle[0]), int(ankle[1])), (255, 200, 100), 3)

        # HUD
        self._draw_hud(img, SD, hip_angle, self.reps[SD], status, idx)

    def _draw_hud(self, img, side, hip_angle, reps, status, idx):
        hud_x = 12
        hud_y = 80 + idx * 110
        rect_w, rect_h = 320, 120
        cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0, 0, 0, 80), -1)

        cv2.putText(img, f"{side} SIDE", (hud_x, hud_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        hip_txt = f"Hip angle: {int(hip_angle)}°" if hip_angle else "Hip angle: -"
        rep_txt = f"Reps: {reps}  Stage: {status}"

        cv2.putText(img, hip_txt, (hud_x, hud_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 220, 200), 2, cv2.LINE_AA)
        cv2.putText(img, rep_txt, (hud_x, hud_y + 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # ----------------------------
    def update(self, img, lm_dict, frame_size):
        sides = ["left", "right"] if self.side == "both" else [self.side]

        current_stage = "unknown"
        for idx, sd in enumerate(sides):
            self._process_side(img, sd, frame_size, lm_dict, idx)
            stage = self.last_stage.get(sd.upper(), "relaxed")
            if current_stage == "unknown":
                current_stage = stage

        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]

        # global overlay
        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        return img, {"reps": total_reps, "stage": current_stage, "feedback": []}
