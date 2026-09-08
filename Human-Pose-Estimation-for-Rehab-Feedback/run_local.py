
# import cv2, os, csv
# from exercises.mini_squat import MiniSquatChecker
# from utils.landmarks import fuse_landmarks
# from yolov8_adapter import YOLOv8PoseWrapper
# import mediapipe as mp
# import json

# from utils.draw import draw_skeleton

# EXERCISE_CHECKERS = {
#     "mini_squat": MiniSquatChecker,
#     # Add other exercise checkers here...
# }

# with open("config.json","r",encoding="utf-8") as f:
#     cfg = json.load(f)

# def run_exercise_live(exercise_name, source=0):
#     EX_CFG = cfg.get(exercise_name, {})
#     checker_cls = EXERCISE_CHECKERS[exercise_name]
#     log_path = f"logs/{exercise_name}_session.csv"
#     os.makedirs("logs", exist_ok=True)
#     logf = open(log_path, "a", newline="", encoding="utf-8")
#     logwriter = csv.writer(logf)
#     if os.stat(log_path).st_size==0:
#         logwriter.writerow(["timestamp","exercise","metric","value","note"])

#     cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
#     W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
#     H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

#     pose_wrapper = YOLOv8PoseWrapper()
#     mp_pose = mp.solutions.pose.Pose(min_detection_confidence=0.6,min_tracking_confidence=0.6)
#     checker = checker_cls(EX_CFG, logger=logwriter)

#     while True:
#         ret, frame = cap.read()
#         if not ret: break
#         img = frame.copy()

#         # landmarks
#         lm_yolo = pose_wrapper.findPose(img, draw=False) or {}
#         res_mp = mp_pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#         lm_mp = {}
#         if res_mp.pose_landmarks:
#             for i,lm in enumerate(res_mp.pose_landmarks.landmark):
#                 lm_mp[mp.solutions.pose.PoseLandmark(i).name]=(lm.x,lm.y,lm.z if hasattr(lm,"z") else 0)
#         lm_dict = fuse_landmarks(lm_yolo,lm_mp)

#         # checker update
#         try:
#             out = checker.update(img,lm_dict,(W,H))
#         except TypeError:
#             out = checker.update(img,lm_dict)
#         if isinstance(out,tuple) and len(out)==2:
#             img,res=out
#         else: img,res=img,out if isinstance(out,dict) else {}

#         draw_skeleton(img,lm_dict,color=(20,200,100),thickness=2,radius=4,exercise=exercise_name)

#         yield img,res

#     cap.release()
#     logf.close()
import cv2, os, csv
import json
from yolov8_adapter import YOLOv8PoseWrapper
import mediapipe as mp

from utils.landmarks import fuse_landmarks
from utils.draw import draw_skeleton

# import all checkers
from exercises.shoulder_flexion import ShoulderFlexionChecker
from exercises.arm_raise_and_carry import ArmRaiseAndCarryChecker
from exercises.mini_squat import MiniSquatChecker
from exercises.wall_calf_stretch import WallCalfStretchChecker
from exercises.straight_leg_raise import StraightLegRaiseChecker
from exercises.kettlebell_swings import KettlebellSwingsChecker
from exercises.seated_hip_internal_rotation import SeatedHipInternalRotationChecker
from exercises.farmers_carry import FarmersCarryChecker
from exercises.bodyweight_deadlift import BodyweightDeadliftChecker
from exercises.single_leg_stance import SingleLegStanceChecker
from exercises.tandem_walk import TandemWalkChecker

# -------------------------------
# EXERCISE CHECKER MAP
# -------------------------------
EXERCISE_CHECKERS = {
    "shoulder_flexion": ShoulderFlexionChecker,
    "arm_raise_and_carry": ArmRaiseAndCarryChecker,
    "mini_squat": MiniSquatChecker,
    "wall_calf_stretch": WallCalfStretchChecker,
    "straight_leg_raise": StraightLegRaiseChecker,
    "kettlebell_swings": KettlebellSwingsChecker,
    "seated_hip_internal_rotation": SeatedHipInternalRotationChecker,
    "farmers_carry": FarmersCarryChecker,
    "bodyweight_deadlift": BodyweightDeadliftChecker,
    "single_leg_stance": SingleLegStanceChecker,
    "tandem_walk": TandemWalkChecker,
}

# -------------------------------
# CONFIG
# -------------------------------
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

# -------------------------------
# LIVE GENERATOR
# -------------------------------
def run_exercise_live(exercise_name, source=0):
    EX_CFG = cfg.get(exercise_name, {})
    checker_cls = EXERCISE_CHECKERS.get(exercise_name)
    if checker_cls is None:
        raise ValueError(f"Exercise '{exercise_name}' not found in EXERCISE_CHECKERS!")

    # Logging
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{exercise_name}_session.csv"
    logf = open(log_path, "a", newline="", encoding="utf-8")
    logwriter = csv.writer(logf)
    if os.stat(log_path).st_size == 0:
        logwriter.writerow(["timestamp", "exercise", "metric", "value", "note"])

    # Video capture
    cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

    # Pose detection
    pose_wrapper = YOLOv8PoseWrapper()
    mp_pose = mp.solutions.pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
    checker = checker_cls(EX_CFG, logger=logwriter)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = frame.copy()

        # --- YOLOv8 landmarks
        lm_yolo = pose_wrapper.findPose(img, draw=False) or {}

        # --- Mediapipe landmarks
        res_mp = mp_pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        lm_mp = {}
        if res_mp.pose_landmarks:
            for i, lm in enumerate(res_mp.pose_landmarks.landmark):
                lm_mp[mp.solutions.pose.PoseLandmark(i).name] = (
                    lm.x, lm.y, lm.z if hasattr(lm, "z") else 0
                )

        # --- Fuse landmarks (YOLOv8 priority)
        lm_dict = fuse_landmarks(lm_yolo, lm_mp)

        # --- Checker update
        try:
            out = checker.update(img, lm_dict, (W, H))
        except TypeError:
            out = checker.update(img, lm_dict)
        if isinstance(out, tuple) and len(out) == 2:
            img, res = out
        else:
            img, res = img, out if isinstance(out, dict) else {}

        # --- Draw skeleton
        draw_skeleton(img, lm_dict, color=(20, 200, 100), thickness=2, radius=4, exercise=exercise_name)

        # --- Yield frame + results for Streamlit
        yield img, res

    cap.release()
    logf.close()
