# exercises/single_leg_stance.py
import cv2
import numpy as np
import math
import time

class SingleLegStanceChecker:
    """
    Single Leg Stance checker.
    Interface: img, res = checker.update(img, lm_dict, frame_size)
    Returns res dict with keys:
      - reps: total completed holds (int)
      - stage: "relaxed"/"holding"/"mixed"/"unknown"
      - hold_time: current hold (float seconds)
      - view: "front" or "side" (heuristic)
      - feedback: list of strings
    """

    def __init__(self, config=None, logger=None):
        c = config or {}
        # thresholds
        self.torso_angle_tol = float(c.get("torso_angle_tol_deg", 12.0))   # degrees to consider upright
        self.sway_tol_px = float(c.get("sway_tol_px", 25.0))               # px to consider sway excessive
        self.min_hold_time = float(c.get("min_hold_sec", 3.0))            # seconds required to count one hold
        self.lift_y_thresh_px = float(c.get("lift_y_thresh_px", 30.0))    # y difference to decide lift
        self.view_shoulder_frac = float(c.get("view_shoulder_frac", 0.15))# fraction of width for front/side heuristic

        self.logger = logger

        # state
        self.active_leg = None              # "LEFT" or "RIGHT" or None
        self.hold_start = None
        self.current_hold = 0.0
        self.ankle_baseline = {"LEFT": None, "RIGHT": None}
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.hold_state = {"LEFT": "relaxed", "RIGHT": "relaxed"}  # "relaxed" / "holding"
        self.last_reported_view = "unknown"

    # ---------- helpers ----------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        if x <= 1.5 and y <= 1.5:
            return (x * W, y * H)
        return (x, y)

    def _get_candidate_keys(self, side, short_name):
        s_up, s_lo = side.upper(), side.lower()
        sn_up, sn_lo = short_name.upper(), short_name.lower()
        variants = [
            f"{s_up}_{sn_up}",
            f"{s_lo}_{sn_lo}",
            f"{s_lo}{sn_lo}",
            f"{sn_up}",
            f"{sn_lo}"
        ]
        # some naming convenience
        if short_name == "foot_index":
            variants += [f"{s_up}_FOOT_INDEX", f"{s_lo}_foot_index", f"{s_up}_FOOTINDEX", f"{s_lo}_footindex"]
        return variants

    def _lookup_point(self, lm_dict, side, name, frame_size):
        for k in self._get_candidate_keys(side, name):
            if k in lm_dict:
                return self._to_pixel(lm_dict[k], frame_size)
        return None

    def _angle_2d(self, a, b, c):
        if not (a and b and c):
            return None
        a = np.array(a, dtype=float); b = np.array(b, dtype=float); c = np.array(c, dtype=float)
        v1 = a - b; v2 = c - b
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return None
        cos = np.dot(v1, v2) / denom
        cos = float(np.clip(cos, -1.0, 1.0))
        ang = math.degrees(math.acos(cos))
        return ang if ang <= 180.0 else 360.0 - ang

    # ---------- view heuristic ----------
    def _detect_view(self, left_sh, right_sh, frame_w):
        # If shoulders span wide horizontally relative to frame width -> front view
        if left_sh and right_sh:
            span = abs(left_sh[0] - right_sh[0])
            if span > frame_w * self.view_shoulder_frac:
                return "front"
            else:
                return "side"
        return "unknown"

    # ---------- update ----------
    def update(self, img, lm_dict, frame_size):
        W, H = frame_size
        now = time.time()
        feedback = []

        # lookup points (pixel coords)
        l_ankle = self._lookup_point(lm_dict, "left", "ankle", frame_size)
        r_ankle = self._lookup_point(lm_dict, "right", "ankle", frame_size)
        l_knee  = self._lookup_point(lm_dict, "left", "knee", frame_size)
        r_knee  = self._lookup_point(lm_dict, "right", "knee", frame_size)
        l_hip   = self._lookup_point(lm_dict, "left", "hip", frame_size)
        r_hip   = self._lookup_point(lm_dict, "right", "hip", frame_size)
        l_shldr = self._lookup_point(lm_dict, "left", "shoulder", frame_size)
        r_shldr = self._lookup_point(lm_dict, "right", "shoulder", frame_size)
        l_wrist = self._lookup_point(lm_dict, "left", "wrist", frame_size)
        r_wrist = self._lookup_point(lm_dict, "right", "wrist", frame_size)

        # detect view
        view = self._detect_view(l_shldr, r_shldr, W)
        self.last_reported_view = view

        # detect active lifted leg:
        active = None
        # prefer ankles; if both present compare y (smaller y -> higher/lifted)
        if l_ankle and r_ankle:
            dy = r_ankle[1] - l_ankle[1]  # positive if right is lower (more down)
            if abs(dy) > self.lift_y_thresh_px:
                # if left ankle is higher (smaller y) => left lifted
                active = "LEFT" if l_ankle[1] < r_ankle[1] else "RIGHT"
        else:
            # fallback: use knee vs hip vertical separation to infer lifted leg (sitting/partial occlusion)
            if l_knee and l_hip and not (r_knee and r_hip):
                # check if left knee is notably higher than hip -> maybe lifted
                if l_knee[1] < l_hip[1] - self.lift_y_thresh_px:
                    active = "LEFT"
            if r_knee and r_hip and not (l_knee and l_hip):
                if r_knee[1] < r_hip[1] - self.lift_y_thresh_px:
                    active = "RIGHT"

        # update hold timer and baseline
        if active:
            if self.active_leg != active:
                self.active_leg = active
                self.hold_start = now
                self.current_hold = 0.0
                # baseline ankle for sway
                if active == "LEFT":
                    self.ankle_baseline["LEFT"] = l_ankle if l_ankle else None
                else:
                    self.ankle_baseline["RIGHT"] = r_ankle if r_ankle else None
                # reset hold_state if switching
                self.hold_state[active] = "relaxed"
            else:
                self.current_hold = now - (self.hold_start or now)
        else:
            # no active leg
            self.active_leg = None
            self.hold_start = None
            self.current_hold = 0.0

        # posture: torso tilt using shoulder midpoint vs hip midpoint
        posture = "unknown"
        if l_shldr and r_shldr and l_hip and r_hip:
            mid_sh = ((l_shldr[0] + r_shldr[0]) / 2.0, (l_shldr[1] + r_shldr[1]) / 2.0)
            mid_hp = ((l_hip[0] + r_hip[0]) / 2.0, (l_hip[1] + r_hip[1]) / 2.0)
            torso_vec = np.array(mid_sh) - np.array(mid_hp)
            # angle from vertical: small => upright
            ang = abs(math.degrees(math.atan2(torso_vec[0], torso_vec[1])))
            posture = "upright" if ang < self.torso_angle_tol else "leaning"
            if posture == "leaning":
                feedback.append(f"Torso leaning ({ang:.1f}°)")

        # sway: if baseline exists and we have current ankle, measure distance
        if self.active_leg:
            SD = self.active_leg
            ref = l_ankle if SD == "LEFT" else r_ankle
            base = self.ankle_baseline[SD]
            if ref and base is not None:
                sway = np.linalg.norm(np.array(ref) - np.array(base))
                if sway > self.sway_tol_px:
                    feedback.append(f"Excessive sway ({sway:.0f}px)")

        # support detection: wrist near image edge (simple heuristic for grabbing chair)
        support = False
        edge_margin = int(W * 0.08)
        for wpt in (l_wrist, r_wrist):
            if wpt:
                if wpt[0] < edge_margin or wpt[0] > (W - edge_margin):
                    support = True
        if support:
            feedback.append("Hand support detected")

        # Completed-hold detection (count a completed hold once when current_hold crosses min_hold_time)
        if self.active_leg:
            SD = self.active_leg
            # only count when posture upright (optional) — counts anyway but easier to require upright:
            posture_ok = (posture == "upright")
            if self.current_hold >= self.min_hold_time and self.hold_state[SD] != "held":
                # mark as held & increment rep
                self.hold_state[SD] = "held"
                self.reps[SD] += 1
                if self.logger:
                    try:
                        self.logger.writerow([
                            time.time(),
                            "single_leg_stance",
                            f"{SD}_hold",
                            self.reps[SD],
                            f"hold={self.current_hold:.1f},view={view}"
                        ])
                    except Exception:
                        pass
            # reset to relaxed when leg dropped
            if self.current_hold < 0.5 and self.hold_state[SD] == "held":
                self.hold_state[SD] = "relaxed"
        else:
            # clear per-side hold_state for both sides when no active
            for k in ("LEFT", "RIGHT"):
                if self.hold_state[k] == "held":
                    # keep held count; do not decrement — but set to relaxed so next hold counts separately
                    self.hold_state[k] = "relaxed"

        # annotate image: joints and HUD
        pts = [l_ankle, r_ankle, l_knee, r_knee, l_hip, r_hip, l_shldr, r_shldr, l_wrist, r_wrist]
        for p in pts:
            if p:
                cv2.circle(img, (int(p[0]), int(p[1])), 5, (60,180,200), -1)
                cv2.circle(img, (int(p[0]), int(p[1])), 8, (0,0,0), 2)

        # top-left HUD
        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]
        cv2.putText(img, f"Total holds: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 4, cv2.LINE_AA)
        cv2.putText(img, f"Total holds: {total_reps}", (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, cv2.LINE_AA)

        # hold/time & view & stage
        stage = "relaxed"
        if self.active_leg:
            stage = "holding" if self.current_hold >= 0.01 else "lifting"
        cv2.putText(img, f"Hold: {self.current_hold:.1f}s", (12, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220,220,220), 2, cv2.LINE_AA)
        cv2.putText(img, f"Stage: {stage}", (12, 84),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,0), 2, cv2.LINE_AA)
        cv2.putText(img, f"View: {view}", (12, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,200,200), 2, cv2.LINE_AA)

        # per-side small HUD
        for idx, sd in enumerate(("LEFT","RIGHT")):
            x = W - 220
            y = 40 + idx * 70
            cv2.putText(img, f"{sd} holds: {self.reps[sd]}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2, cv2.LINE_AA)
            st = self.hold_state[sd]
            cv2.putText(img, f"state:{st}", (x, y+22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1, cv2.LINE_AA)

        # return a standardized dict so run_local.py displays correctly
        result = {
            "reps": total_reps,
            "stage": stage,
            "hold_time": round(self.current_hold, 1),
            "view": view,
            "feedback": feedback
        }
        return img, result
