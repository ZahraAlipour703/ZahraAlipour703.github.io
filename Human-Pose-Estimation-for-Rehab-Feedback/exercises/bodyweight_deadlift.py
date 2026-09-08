# exercises/bodyweight_deadlift.py
import cv2
import numpy as np
import math
import time

class BodyweightDeadliftChecker:
    """
    Bodyweight Deadlift checker (suitable for seated/standing variations).
    Interface:
        checker = BodyweightDeadliftChecker(config, logger=csv_writer)
        img, res = checker.update(img, lm_dict, (frame_W, frame_H))
    Returns res: {"reps": int, "stage": str, "feedback": [str,...]}
    """

    def __init__(self, config=None, logger=None):
        c = config or {}
        self.side = c.get("side", "both").lower()   # "left", "right", or "both"
        # angle thresholds (degrees). Tune to camera/setup if needed.
        # Hip angle = angle at HIP formed by SHOULDER - HIP - KNEE
        self.down_hip_angle = float(c.get("down_hip_angle_deg", 120.0))   # considered "hinged"/down when <= this
        self.up_hip_angle = float(c.get("up_hip_angle_deg", 165.0))       # considered "standing"/up when >= this
        self.tol = float(c.get("tolerance_deg", 6.0))

        # knee constraint (to ensure not turning into a squat)
        self.max_knee_flexion_for_deadlift = float(c.get("max_knee_flexion_deg", 120.0))
        # back slacking detection (pixel units threshold)
        self.back_slack_px_tol = float(c.get("back_slack_px_tol", 7.0))

        # state per-side
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "up", "RIGHT": "up"}   # start assuming standing/up
        self.initial_back_len = {"LEFT": None, "RIGHT": None}

        self.logger = logger

    # -------------------------
    # helpers (naming variants + normalization)
    # -------------------------
    def _to_pixel(self, pt, frame_size):
        if pt is None:
            return None
        W, H = frame_size
        x, y = float(pt[0]), float(pt[1])
        # if normalized coords (0..1) -> convert
        if x <= 1.5 and y <= 1.5:
            return (x * W, y * H)
        return (x, y)

    def _get_candidate_keys(self, side, short_name):
        s_up = side.upper()
        s_lo = side.lower()
        sn_up = short_name.upper()
        sn_lo = short_name.lower()
        variants = [
            f"{s_up}_{sn_up}",
            f"{s_lo}_{sn_lo}",
            f"{s_lo}{sn_lo}",
            f"{sn_up}",
            f"{sn_lo}"
        ]
        if short_name == "foot_index":
            variants += [f"{s_up}_FOOT_INDEX", f"{s_lo}_foot_index", f"{s_up}_FOOTINDEX", f"{s_lo}_footindex"]
        return variants

    def _lookup_point(self, lm_dict, side, name, frame_size):
        for k in self._get_candidate_keys(side, name):
            if k in lm_dict:
                return self._to_pixel(lm_dict[k], frame_size)
        return None

    def _angle_2d(self, a, b, c):
        """Angle at b formed by a-b-c (2D pixel coords). Returns degrees or None."""
        if not (a and b and c):
            return None
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        c = np.array(c, dtype=float)
        v1 = a - b
        v2 = c - b
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return None
        cosang = np.dot(v1, v2) / denom
        cosang = float(np.clip(cosang, -1.0, 1.0))
        ang = math.degrees(math.acos(cosang))
        return ang if ang <= 180.0 else 360.0 - ang

    # -------------------------
    # baseline initialization: back length for "slacking" check
    # -------------------------
    def _init_back_len_if_needed(self, side, shoulder, hip):
        SD = side.upper()
        if self.initial_back_len[SD] is None and shoulder is not None and hip is not None:
            self.initial_back_len[SD] = float(np.linalg.norm(np.array(shoulder) - np.array(hip)))

    # -------------------------
    # side processing
    # -------------------------
    def _process_side(self, img, side, frame_size, lm_dict, idx):
        SD = side.upper()

        # Lookup commonly used joints (support multiple naming conventions)
        shoulder = self._lookup_point(lm_dict, side, "shoulder", frame_size)
        hip = self._lookup_point(lm_dict, side, "hip", frame_size)
        knee = self._lookup_point(lm_dict, side, "knee", frame_size)
        ankle = self._lookup_point(lm_dict, side, "ankle", frame_size)
        heel = self._lookup_point(lm_dict, side, "heel", frame_size)
        # also check wrist/hand for posture hints (optional)
        wrist = self._lookup_point(lm_dict, side, "wrist", frame_size)
        elbow = self._lookup_point(lm_dict, side, "elbow", frame_size)

        feedback = []
        hip_angle = None
        knee_angle = None
        status = self.last_stage[SD]

        # compute angles (pixel coords)
        if shoulder and hip and knee:
            hip_angle = self._angle_2d(shoulder, hip, knee)   # shoulder-hip-knee
        if hip and knee and ankle:
            knee_angle = self._angle_2d(hip, knee, ankle)

        # initialize back length when user stands straight (hip angle near up)
        if hip_angle is not None and hip_angle >= (self.up_hip_angle - self.tol):
            self._init_back_len_if_needed(side, shoulder, hip)

        # form checks
        if self.initial_back_len[SD] is not None and shoulder is not None and hip is not None:
            cur_back_len = float(np.linalg.norm(np.array(shoulder) - np.array(hip)))
            if cur_back_len + self.back_slack_px_tol < self.initial_back_len[SD]:
                feedback.append("Spine flexion (back slacking)")

        if knee_angle is not None and knee_angle < self.max_knee_flexion_for_deadlift:
            # knee bending too much (turning into squat)
            feedback.append("Too much knee bend (prefer hip hinge)")

        # state machine (hysteresis)
        # enter "down" when hip angle <= down_hip_angle - tol
        # return to "up" when hip angle >= up_hip_angle + tol -> count rep (only if no serious feedback)
        if hip_angle is not None:
            if hip_angle <= (self.down_hip_angle - self.tol):
                # went down (hinge)
                if self.last_stage[SD] != "down":
                    self.last_stage[SD] = "down"
                status = "down"
            elif hip_angle >= (self.up_hip_angle + self.tol):
                # returned up
                if self.last_stage[SD] == "down":
                    # only count when no blocking feedback (spine slacking or large knee bend)
                    blocking = [f for f in feedback if "Spine flexion" in f or "Too much knee" in f]
                    if len(blocking) == 0:
                        self.reps[SD] += 1
                        if self.logger:
                            try:
                                self.logger.writerow([time.time(), "bodyweight_deadlift", f"{SD}_rep_done", self.reps[SD],
                                                      f"hip={hip_angle:.1f},knee={knee_angle:.1f}" if knee_angle is not None else f"hip={hip_angle:.1f}"])
                            except Exception:
                                pass
                    # always set stage to up after return
                    self.last_stage[SD] = "up"
                status = "up"

        # annotate joints + skeleton lines for clarity
        for pt in (shoulder, hip, knee, ankle, heel, elbow, wrist):
            if pt:
                cv2.circle(img, (int(pt[0]), int(pt[1])), 5, (60,160,220), -1)
                cv2.circle(img, (int(pt[0]), int(pt[1])), 8, (0,0,0), 2)

        def L(a,b):
            if a and b:
                cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (200,220,255), 3)
        L(shoulder, hip)
        L(hip, knee)
        L(knee, ankle)

        # HUD for this side
        hud_x = 12
        hud_y = 80 + idx * 110
        rect_w, rect_h = 300, 90
        cv2.rectangle(img, (hud_x - 8, hud_y - 22), (hud_x + rect_w, hud_y + rect_h), (0,0,0,80), -1)
        cv2.putText(img, f"{SD} SIDE", (hud_x, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
        hip_txt = f"Hip: {int(hip_angle)}°" if hip_angle is not None else "Hip: -"
        knee_txt = f"Knee: {int(knee_angle)}°" if knee_angle is not None else "Knee: -"
        rep_txt = f"Reps: {self.reps[SD]}  Stage: {status}"
        cv2.putText(img, hip_txt, (hud_x, hud_y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,220,200), 2, cv2.LINE_AA)
        cv2.putText(img, knee_txt, (hud_x, hud_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200,220,200), 2, cv2.LINE_AA)
        cv2.putText(img, rep_txt, (hud_x + 140, hud_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

        wy = hud_y + 72
        for f in feedback:
            cv2.putText(img, f"⚠ {f}", (hud_x, wy), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2, cv2.LINE_AA)
            wy += 18

        return feedback, status

    # -------------------------
    # public update: unified interface
    # -------------------------
    def update(self, img, lm_dict, frame_size):
        """
        img: BGR image (will be annotated).
        lm_dict: fused landmarks dict (names -> (x,y[,z]) normalized or pixel).
        frame_size: (W,H)
        returns: (img_annotated, {"reps":int, "stage":str, "feedback":[...]})
        """
        sides = ["left", "right"] if self.side == "both" else [self.side]
        total_feedback = []
        current_stage = "unknown"

        for idx, sd in enumerate(sides):
            fb, stage = self._process_side(img, sd, frame_size, lm_dict, idx)
            total_feedback += [*fb]
            if current_stage == "unknown":
                current_stage = stage

        total_reps = self.reps["LEFT"] + self.reps["RIGHT"]
        # global total overlay (big)
        cv2.putText(img, f"Deadlifts Total: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0,0,0), 4, cv2.LINE_AA)
        cv2.putText(img, f"Deadlifts Total: {total_reps}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255,255,255), 2, cv2.LINE_AA)

        return img, {"reps": total_reps, "stage": current_stage, "feedback": total_feedback}
