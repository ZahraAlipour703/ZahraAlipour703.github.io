
import cv2
import numpy as np
import math
import time
from collections import deque


class SeatedHipInternalRotationChecker:
    """
    Seated Hip Internal Rotation exercise tracker.

    Detects and counts repetitions of internal hip rotation by tracking
    the horizontal motion of the ankle relative to the knee.
    """

    def __init__(self, config=None, logger=None):
        c = config or {}
        self.side = c.get("side", "both").lower()   # "left", "right", or "both"

        # thresholds (normalized horizontal offset)
        self.rotation_thresh = float(c.get("rotation_thresh", 0.25))   # rotated if ankle moves >25% of leg length
        self.neutral_thresh = float(c.get("neutral_thresh", 0.10))     # neutral if within 10% of leg length
        self.tolerance = float(c.get("tolerance", 0.02))

        self.smooth_window = int(c.get("smoothing_window", 3))
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "neutral", "RIGHT": "neutral"}
        self._buf = {"LEFT": deque(maxlen=self.smooth_window), "RIGHT": deque(maxlen=self.smooth_window)}
        self.logger = logger

    # ----------------------
    # Helpers
    # ----------------------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        if x <= 1.5 and y <= 1.5:  # normalized coords
            return (x * W, y * H)
        return (x, y)

    def _lookup_point(self, lm_dict, side, name, frame_size):
        candidates = [
            f"{side.upper()}_{name.upper()}",
            f"{side.lower()}_{name.lower()}",
            name.upper(),
            name.lower(),
        ]
        for k in candidates:
            if k in lm_dict:
                return self._to_pixel(lm_dict[k], frame_size)
        return None

    # ----------------------
    # Process one side
    # ----------------------
    def _process_side(self, img, side, frame_size, lm_dict, idx):
        SD = side.upper()
        hip = self._lookup_point(lm_dict, side, "hip", frame_size)
        knee = self._lookup_point(lm_dict, side, "knee", frame_size)
        ankle = self._lookup_point(lm_dict, side, "ankle", frame_size)

        feedback = []
        rotation_val = None
        stage = self.last_stage[SD]

        if hip and knee and ankle:
            leg_len = np.linalg.norm(np.array(knee) - np.array(hip))
            delta_x = (ankle[0] - knee[0]) / (leg_len + 1e-6)  # normalized horizontal shift
            self._buf[SD].append(delta_x)
            rotation_val = float(sum(self._buf[SD]) / len(self._buf[SD]))

            # --- State machine with hysteresis ---
            if abs(rotation_val) > (self.rotation_thresh + self.tolerance) and self.last_stage[SD] == "neutral":
                self.last_stage[SD] = "rotated"
                stage = "rotated"

            elif abs(rotation_val) < (self.neutral_thresh - self.tolerance) and self.last_stage[SD] == "rotated":
                self.reps[SD] += 1
                self.last_stage[SD] = "neutral"
                stage = "neutral"

                if self.logger:
                    try:
                        self.logger.writerow([
                            time.time(),
                            "seated_hip_internal_rotation",
                            f"{SD}_rep_done",
                            self.reps[SD],
                            f"rotation={rotation_val:.2f}"
                        ])
                    except Exception:
                        pass

        else:
            feedback.append("Missing keypoints")

        # Draw body parts
        for pt in (hip, knee, ankle):
            if pt:
                cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (30, 180, 255), -1)
                cv2.circle(img, (int(pt[0]), int(pt[1])), 8, (0, 0, 0), 2)
        if hip and knee:
            cv2.line(img, (int(hip[0]), int(hip[1])), (int(knee[0]), int(knee[1])), (200, 220, 200), 2)
        if knee and ankle:
            cv2.line(img, (int(knee[0]), int(knee[1])), (int(ankle[0]), int(ankle[1])), (200, 220, 200), 2)

        self._draw_hud(img, SD, rotation_val, self.reps[SD], stage, feedback, idx)

        return rotation_val, feedback

    # ----------------------
    # HUD
    # ----------------------
    def _draw_hud(self, img, side, rotation_val, reps, stage, feedback, idx):
        hud_x, hud_y = 12, 80 + idx * 120
        rect_w, rect_h = 300, 110
        cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0, 0, 0, 80), -1)

        cv2.putText(img, f"{side} SIDE", (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        rot_txt = f"Rot: {rotation_val:+.2f}" if rotation_val is not None else "Rot: -"
        rep_txt = f"Reps: {reps}  Stage: {stage}"

        cv2.putText(img, rot_txt, (hud_x, hud_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 220, 200), 2, cv2.LINE_AA)
        cv2.putText(img, rep_txt, (hud_x, hud_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        wy = hud_y + 84
        for r in feedback:
            cv2.putText(img, f"⚠ {r}", (hud_x, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
            wy += 18

    # ----------------------
    # public update
    # ----------------------
    def update(self, img, lm_dict, frame_size):
        sides = ["left", "right"] if self.side == "both" else [self.side]
        total_feedback = []
        any_stage = "neutral"

        for idx, sd in enumerate(sides):
            rotation_val, fb = self._process_side(img, sd, frame_size, lm_dict, idx)
            total_feedback.extend(fb)
            stage_candidate = self.last_stage.get(sd.upper(), "neutral")
            if any_stage == "neutral" and stage_candidate == "rotated":
                any_stage = "rotated"

        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]

        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, f"Total reps: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        return img, {"reps": total_reps, "stage": any_stage, "feedback": total_feedback}
