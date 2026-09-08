import cv2
import numpy as np
import math
import time
from collections import deque

class TandemWalkChecker:
    """
    Tandem walk step counter + posture monitor.

    Usage:
        checker = TandemWalkChecker(config, logger=csv_writer)
        img, res = checker.update(img, lm_dict, (frame_width, frame_height))

    res -> {"left_steps": int, "right_steps": int, "total_steps": int,
            "view": "front"/"side"/"unknown", "last_step_time": float, "feedback": [...]}
    """

    def __init__(self, config=None, logger=None):
        c = config or {}
        # Appearance / thresholds
        self.shoulder_front_thresh = float(c.get("shoulder_front_thresh", 0.18))  # fraction of width
        self.crossing_thresh_px = float(c.get("crossing_thresh_px", 8))          # minimal crossing distance to count
        self.debounce_sec = float(c.get("step_debounce_sec", 0.35))              # minimal time between step counts
        self.smoothing_window = int(c.get("smoothing_window", 3))                # smoothing for diff signal
        self.sway_tol_px = float(c.get("sway_tol_px", 80))                       # large sway warning
        self.support_dist_px = float(c.get("support_dist_px", 40))              # wrist near edge -> support

        self.logger = logger

        # state
        self.left_steps = 0
        self.right_steps = 0
        self.prev_diff = None               # previous (left_axis - right_axis)
        self.diff_history = deque(maxlen=self.smoothing_window)
        self.last_step_time = 0.0
        self.last_cross_side = None         # 'LEFT' or 'RIGHT' last counted
        self.ankle_baseline = {"LEFT": None, "RIGHT": None}
        self.last_view = "unknown"

    # ---------------- helpers ----------------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        try:
            x = float(pt[0]); y = float(pt[1])
        except Exception:
            return None
        if x <= 1.5 and y <= 1.5:
            return (x * W, y * H)
        return (x, y)

    def _get_candidate_keys(self, side, short_name):
        s_up = side.upper(); s_lo = side.lower(); sn_up = short_name.upper(); sn_lo = short_name.lower()
        variants = [
            f"{s_up}_{sn_up}",
            f"{s_lo}_{sn_lo}",
            f"{s_lo}{sn_lo}",
            f"{sn_up}",
            f"{sn_lo}"
        ]
        # special aliases
        if short_name == "foot_index":
            variants += [f"{s_up}_FOOT_INDEX", f"{s_lo}_foot_index", f"{s_up}_FOOTINDEX", f"{s_lo}_footindex"]
        if short_name == "index":
            variants += [f"{s_up}_INDEX", f"{s_lo}_index"]
        return variants

    def _lookup_point(self, lm_dict, side, name, frame_size):
        for k in self._get_candidate_keys(side, name):
            if k in lm_dict:
                return self._to_pixel(lm_dict[k], frame_size)
        return None

    def _axis_val(self, pt, axis):
        # axis == "x" or "y"
        return pt[0] if axis == "x" else pt[1]

    # ---------------- view detection ----------------
    def _detect_view(self, left_sh, right_sh, nose, frame_w):
        """
        Heuristic to detect front vs side:
         - if shoulder horizontal separation is sufficiently large -> front
         - else side
         - nose between shoulders also indicates front
        """
        if left_sh is None or right_sh is None:
            return "unknown"
        shoulder_dx = abs(left_sh[0] - right_sh[0])
        norm = shoulder_dx / float(frame_w + 1e-8)
        if norm >= self.shoulder_front_thresh:
            return "front"
        # nose heuristic
        if nose is not None:
            if min(left_sh[0], right_sh[0]) <= nose[0] <= max(left_sh[0], right_sh[0]):
                return "front"
        return "side"

    # ---------------- step detection ----------------
    def _update_crossing(self, left_axis, right_axis, now):
        """
        Detect crossing event (sign change of left_axis - right_axis).
        When sign changes and value magnitude > crossing_thresh_px and debounce passes,
        we count a step for the foot that moved ahead.
        """
        if left_axis is None or right_axis is None:
            self.prev_diff = None
            self.diff_history.clear()
            return None  # no event

        cur_diff = float(left_axis - right_axis)
        # smoothing
        self.diff_history.append(cur_diff)
        cur = float(sum(self.diff_history) / len(self.diff_history))

        if self.prev_diff is None:
            self.prev_diff = cur
            return None

        # crossing if sign changed and magnitude large enough
        if (self.prev_diff * cur) < 0 and abs(cur) >= self.crossing_thresh_px:
            # debounce
            if now - self.last_step_time >= self.debounce_sec:
                # determine which foot is ahead now
                # cur < 0 -> left_axis < right_axis -> left is "less" than right along axis
                foot = "LEFT" if cur < 0 else "RIGHT"
                self.last_step_time = now
                self.prev_diff = cur
                self.diff_history.clear()
                return foot
        # update previous
        self.prev_diff = cur
        return None

    # ---------------- update per frame ----------------
    def update(self, img, lm_dict, frame_size):
        W, H = frame_size
        now = time.time()
        feedback = []

        # lookup keypoints (pixel coords)
        left_sh = self._lookup_point(lm_dict, "left", "shoulder", frame_size)
        right_sh = self._lookup_point(lm_dict, "right", "shoulder", frame_size)
        nose = None
        # try several nose keys
        for nk in ("NOSE", "nose"):
            if nk in lm_dict:
                nose = self._to_pixel(lm_dict[nk], frame_size); break

        l_ankle = self._lookup_point(lm_dict, "left", "ankle", frame_size)
        r_ankle = self._lookup_point(lm_dict, "right", "ankle", frame_size)
        l_wrist = self._lookup_point(lm_dict, "left", "wrist", frame_size)
        r_wrist = self._lookup_point(lm_dict, "right", "wrist", frame_size)

        # detect view (front or side)
        view = self._detect_view(left_sh, right_sh, nose, W)
        self.last_view = view

        # pick axis for comparison: front -> y axis (vertical), side -> x axis (horizontal)
        # axis = "y" if view == "front" else "x"

        # # convert ankles to axis values (None-safe)
        # left_axis = self._axis_val(l_ankle, axis) if l_ankle else None
        # right_axis = self._axis_val(r_ankle, axis) if r_ankle else None
        # axis choice: front view -> compare X separation, side view -> compare Y (vertical progression)
        if view == "front":
            axis = "x"
        else:
            axis = "y"

        left_axis = self._axis_val(l_ankle, axis) if l_ankle else None
        right_axis = self._axis_val(r_ankle, axis) if r_ankle else None


        # step detection via crossing
        foot = self._update_crossing(left_axis, right_axis, now)
        if foot == "LEFT":
            self.left_steps += 1
            self.last_cross_side = "LEFT"
            if self.logger:
                try: self.logger.writerow([now, "tandem_walk", "left_step", self.left_steps, "cross"]) 
                except Exception: pass
        elif foot == "RIGHT":
            self.right_steps += 1
            self.last_cross_side = "RIGHT"
            if self.logger:
                try: self.logger.writerow([now, "tandem_walk", "right_step", self.right_steps, "cross"])
                except Exception: pass

        total_steps = self.left_steps + self.right_steps

        # simple sway detection: measure instantaneous ankle displacement from baseline (first frame when active)
        sway_warning = False
        if l_ankle and self.ankle_baseline["LEFT"] is None:
            self.ankle_baseline["LEFT"] = l_ankle
        if r_ankle and self.ankle_baseline["RIGHT"] is None:
            self.ankle_baseline["RIGHT"] = r_ankle

        if self.ankle_baseline["LEFT"] and l_ankle:
            d = np.linalg.norm(np.array(l_ankle) - np.array(self.ankle_baseline["LEFT"]))
            if d > self.sway_tol_px:
                sway_warning = True
                feedback.append(f"Excessive sway L ({int(d)}px)")
        if self.ankle_baseline["RIGHT"] and r_ankle:
            d = np.linalg.norm(np.array(r_ankle) - np.array(self.ankle_baseline["RIGHT"]))
            if d > self.sway_tol_px:
                sway_warning = True
                feedback.append(f"Excessive sway R ({int(d)}px)")

        # support detection: wrist near left/right image edge -> using support_dist_px
        support = False
        if l_wrist and (l_wrist[0] < self.support_dist_px or l_wrist[0] > (W - self.support_dist_px)):
            support = True; feedback.append("Left hand near support")
        if r_wrist and (r_wrist[0] < self.support_dist_px or r_wrist[0] > (W - self.support_dist_px)):
            support = True; feedback.append("Right hand near support")

        # --------- visualization (minimal / non-crowded) ----------
        # small joints for relevant points only
        J_COLOR = (30, 200, 160)
        for pt in (left_sh, right_sh, l_ankle, r_ankle, l_wrist, r_wrist, nose):
            if pt:
                cv2.circle(img, (int(pt[0]), int(pt[1])), 4, J_COLOR, -1)

        # thin skeleton lines for ankles only
        if l_ankle and r_ankle:
            cv2.line(img, (int(l_ankle[0]), int(l_ankle[1])), (int(r_ankle[0]), int(r_ankle[1])), (200,220,255), 2)

        # HUD: compact top-left (view + total steps)
        hud_x, hud_y = 12, 18
        txt1 = f"View:{view}  Total steps:{total_steps}"
        cv2.putText(img, txt1, (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 4, cv2.LINE_AA)
        cv2.putText(img, txt1, (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

        # RHS per-side step counters (small)
        cv2.putText(img, f"LEFT steps: {self.left_steps}", (W-170, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(img, f"RIGHT steps: {self.right_steps}", (W-170, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

        # feedback lines under HUD (up to 3)
        fy = hud_y + 24
        for msg in feedback[:3]:
            cv2.putText(img, msg, (hud_x, fy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,50,200), 2, cv2.LINE_AA)
            fy += 18

        # return structured result
        result = {
            "left_steps": self.left_steps,
            "right_steps": self.right_steps,
            "total_steps": total_steps,
            "view": view,
            "last_step_time": self.last_step_time,
            "feedback": feedback
        }
        return img, result
