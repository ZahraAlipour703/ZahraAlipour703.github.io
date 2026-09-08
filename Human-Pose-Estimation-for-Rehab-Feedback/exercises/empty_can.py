# exercises/empty_can.py
import time, math
from exercises.base import BaseExerciseChecker
from utils.angles import angle_between_3d
from utils.smoothing import SimpleSmoother
from utils.landmarks import landmarks_to_dict

class EmptyCanChecker(BaseExerciseChecker):
    """
    Empty Can exercise (30° abduction, thumb pointing down / hand rotated down).
    Detects lateral raise to about 30° in the scapular plane and checks that
    the forearm/hand is externally rotated so the thumb points downwards (empty-can).
    Counts reps when patient reaches the target and holds for hold_time_sec.

    Config keys under "empty_can":
      side: "both"/"left"/"right"
      target_angle_up: (deg) recommended ~30 (we use 30..50)
      target_angle_down: (deg) rest baseline ~10..40 depending on setup
      tolerance_deg: angle tolerance for up/down detection
      hold_time_sec: seconds to hold at top to count a rep
      smoothing_window: smoother window size
      min_moving_angle: threshold for 'moving' vs idle
      max_torso_tilt_deg: allow some but not too much torso lean
      max_elbow_flexion_deg: allowed elbow bend (should be near 0)
      rotation_threshold_deg: how strict we are about thumb-down rotation
    """

    def __init__(self, config, logger=None):
        super().__init__("empty_can", config, logger)
        c = config or {}

        self.side = c.get("side", "both").lower()
        self.target_up = float(c.get("target_angle_up", 30.0))
        self.target_down = float(c.get("target_angle_down", 10.0))
        self.tol = float(c.get("tolerance_deg", 12.0))
        self.hold_time = float(c.get("hold_time_sec", 1.5))
        self.smoother_window = int(c.get("smoothing_window", 5))
        self.min_moving_angle = float(c.get("min_moving_angle", 6.0))

        self.max_torso_tilt = float(c.get("max_torso_tilt_deg", 18.0))
        self.max_elbow_flexion = float(c.get("max_elbow_flexion_deg", 25.0))

        # rotation: we expect the forearm/palm rotated so thumb points downwards.
        # rotation_threshold_deg: how close to the ideal rotation (thumb-down) to accept.
        self.rotation_threshold_deg = float(c.get("rotation_threshold_deg", 35.0))

        # state
        self.smoothers = {"LEFT": SimpleSmoother(self.smoother_window),
                          "RIGHT": SimpleSmoother(self.smoother_window)}
        self.hold_start = {"LEFT": None, "RIGHT": None}
        self.reps = {"LEFT": 0, "RIGHT": 0}
        self.last_stage = {"LEFT": "down", "RIGHT": "down"}
        self.last_update_time = None

    def _get_quads(self, dt):
        """
        Return required joints per side: hip, shoulder, elbow, wrist, index_mcp, thumb_cmc
        index_mcp and thumb_cmc are used to estimate hand orientation/rotation.
        """
        pairs = {}
        if "RIGHT_SHOULDER" in dt:
            pairs["RIGHT"] = {
                "hip": dt.get("RIGHT_HIP"),
                "shoulder": dt.get("RIGHT_SHOULDER"),
                "elbow": dt.get("RIGHT_ELBOW"),
                "wrist": dt.get("RIGHT_WRIST"),
                # optional hand points
                "index_mcp": dt.get("RIGHT_INDEX_FINGER_MCP"),
                "thumb_cmc": dt.get("RIGHT_THUMB_CMC")
            }
        if "LEFT_SHOULDER" in dt:
            pairs["LEFT"] = {
                "hip": dt.get("LEFT_HIP"),
                "shoulder": dt.get("LEFT_SHOULDER"),
                "elbow": dt.get("LEFT_ELBOW"),
                "wrist": dt.get("LEFT_WRIST"),
                "index_mcp": dt.get("LEFT_INDEX_FINGER_MCP"),
                "thumb_cmc": dt.get("LEFT_THUMB_CMC")
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

    def _estimate_thumb_down_rotation(self, elbow, wrist, index_mcp, thumb_cmc):
        """
        Heuristic estimate of palm rotation (pronation/rotation).
        Approach:
          - vector forearm = wrist - elbow
          - vector from wrist to index_mcp (or thumb base) approximates palm direction
          - compute angle between forearm vector and palm-normal-like vector projected in plane perpendicular to forearm
        We return a value in degrees where 0 means "neutral" and positive indicates rotation consistent with thumb-down.
        NOTE: This is heuristic — camera viewpoint and 2D projection limit accuracy.
        """
        try:
            # require points
            if not (elbow and wrist and index_mcp and thumb_cmc):
                return None
            # 3D vectors
            fe = (wrist[0]-elbow[0], wrist[1]-elbow[1], wrist[2]-elbow[2])
            wf = (index_mcp[0]-wrist[0], index_mcp[1]-wrist[1], index_mcp[2]-wrist[2])
            # compute cross product = approximate palm normal
            nx = fe[1]*wf[2] - fe[2]*wf[1]
            ny = fe[2]*wf[0] - fe[0]*wf[2]
            nz = fe[0]*wf[1] - fe[1]*wf[0]
            # measure how much the palm-normal points "down" relative to camera up axis:
            # approximate: dot of palm-normal with world+Y (image y axis increases downward)
            # because coordinates are normalized image coords where y increases downward,
            # a palm-normal with positive y component suggests the thumb faces downwards for certain poses.
            # We'll compute a simple rotation metric from ny (normalized).
            n_norm = math.sqrt(nx*nx + ny*ny + nz*nz) + 1e-8
            ny_n = ny / n_norm
            # convert to degrees-ish scale (0..90)
            rot_deg = abs(ny_n) * 90.0
            return rot_deg
        except Exception:
            return None

    def update(self, raw_landmarks, t=None):
        now = t or time.time()
        # delta time (fps independent timers)
        dt_time = 0.0
        if self.last_update_time is not None:
            dt_time = now - self.last_update_time
        self.last_update_time = now

        dt = landmarks_to_dict(raw_landmarks)
        if not dt:
            self.state = "no_pose"
            return {"status": "no_pose", "per_side": {}}

        torso_tilt = self._torso_tilt(dt)
        quads = self._get_quads(dt)
        results = {"per_side": {}, "torso_tilt_deg": torso_tilt}

        sides = ["LEFT","RIGHT"] if self.side == "both" else ([self.side.upper()])

        for sd in sides:
            info = quads.get(sd)
            if not info or not info.get("hip") or not info.get("shoulder") or not info.get("elbow") or not info.get("wrist"):
                results["per_side"][sd] = {"status":"no_pose"}
                continue

            hip = info["hip"]; sh = info["shoulder"]; el = info["elbow"]; wr = info["wrist"]
            idx = info.get("index_mcp"); th = info.get("thumb_cmc")

            # main abduction angle (hip - shoulder - elbow)
            ang = angle_between_3d(hip, sh, el)
            ang_s = self.smoothers[sd].update(ang)

            # elbow flexion
            elbow_ang = angle_between_3d(sh, el, wr)
            elbow_flexion = max(0.0, 180.0 - elbow_ang)

            # rotation estimate (thumb down)
            rot_deg = self._estimate_thumb_down_rotation(el, wr, idx, th)

            # collect reasons
            reasons = []
            if elbow_flexion > self.max_elbow_flexion:
                reasons.append(f"Elbow bent {elbow_flexion:.0f}° > {self.max_elbow_flexion:.0f}°")
            if torso_tilt is not None and torso_tilt > self.max_torso_tilt:
                reasons.append(f"Torso tilt {torso_tilt:.0f}° > {self.max_torso_tilt:.0f}°")
            if rot_deg is None:
                # cannot estimate rotation — don't be overly strict, but warn
                reasons.append("Hand orientation unclear")
            elif rot_deg < self.rotation_threshold_deg:
                # rot_deg small => palm-normal not aligned as expected for thumb-down
                reasons.append("Rotate hand so thumb points down")

            # rep/hold logic (abduction to ~30°)
            if ang_s >= self.target_up - self.tol:
                # candidate up
                if self.hold_start[sd] is None:
                    self.hold_start[sd] = now
                elapsed = now - self.hold_start[sd]
                if elapsed >= self.hold_time:
                    if self.last_stage[sd] != "up_done":
                        # only count if no critical reasons (but allow soft warnings)
                        # treat "Hand orientation unclear" as soft (still count) but rotation warning prevents counting
                        blocking = [r for r in reasons if r.startswith("Elbow bent") or r.startswith("Torso tilt") or r.startswith("Rotate hand")]
                        if len(blocking) == 0:
                            # good rep
                            self.reps[sd] += 1
                            if self.logger:
                                self.log(f"{sd}_rep_done", self.reps[sd], note=f"angle={ang_s:.1f}, rot={rot_deg if rot_deg else -1:.1f}")
                            self.last_stage[sd] = "up_done"
                            results["per_side"][sd] = {
                                "status":"done", "angle": ang_s, "elbow_flexion": elbow_flexion,
                                "rotation_deg": rot_deg, "reasons": reasons, "reps": self.reps[sd], "hold_elapsed": elapsed
                            }
                        else:
                            # reached top but some blocking reason exists — mark holding_bad_form
                            results["per_side"][sd] = {
                                "status":"holding_bad_form", "angle": ang_s, "elbow_flexion": elbow_flexion,
                                "rotation_deg": rot_deg, "reasons": reasons, "hold_elapsed": elapsed
                            }
                    else:
                        results["per_side"][sd] = {
                            "status":"done", "angle": ang_s, "elbow_flexion": elbow_flexion,
                            "rotation_deg": rot_deg, "reasons": reasons, "reps": self.reps[sd]
                        }
                else:
                    results["per_side"][sd] = {
                        "status":"holding", "angle": ang_s, "elbow_flexion": elbow_flexion,
                        "rotation_deg": rot_deg, "reasons": reasons, "hold_elapsed": elapsed
                    }
            elif ang_s <= self.target_down + self.tol:
                # down position -> reset hold timer and stages
                self.hold_start[sd] = None
                if self.last_stage[sd] == "up_done":
                    self.last_stage[sd] = "down"
                results["per_side"][sd] = {"status":"down", "angle": ang_s, "elbow_flexion": elbow_flexion, "rotation_deg": rot_deg, "reasons": reasons}
            else:
                # moving
                self.hold_start[sd] = None
                if ang_s > self.min_moving_angle:
                    results["per_side"][sd] = {"status":"moving", "angle": ang_s, "elbow_flexion": elbow_flexion, "rotation_deg": rot_deg, "reasons": reasons}
                else:
                    results["per_side"][sd] = {"status":"idle", "angle": ang_s, "elbow_flexion": elbow_flexion, "rotation_deg": rot_deg, "reasons": reasons}

        return results
