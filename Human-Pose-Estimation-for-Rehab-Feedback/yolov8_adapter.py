# # yolov8_adapter.py
# # Adapter that loads a YOLOv8 pose model and provides a `findPose(frame, draw=False)`-like API.
# # Returns a dictionary mapping landmark names (e.g. LEFT_SHOULDER) -> (x_norm, y_norm, z_norm)
# # normalized coordinates are in [0..1] relative to frame width/height.
# # z is a weak depth cue (0 if unavailable) so drawing can use it for "3D" effects.

# import numpy as np
# import cv2

# try:
#     from ultralytics import YOLO
# except Exception as e:
#     YOLO = None
#     # user will see a clear error when trying to use this adapter

# # COCO-17 keypoint index -> name mapping (common for YOLOv8 pose outputs)
# COCO17_IDX_TO_NAME = {
#     0: "NOSE",
#     1: "LEFT_EYE",
#     2: "RIGHT_EYE",
#     3: "LEFT_EAR",
#     4: "RIGHT_EAR",
#     5: "LEFT_SHOULDER",
#     6: "RIGHT_SHOULDER",
#     7: "LEFT_ELBOW",
#     8: "RIGHT_ELBOW",
#     9: "LEFT_WRIST",
#     10: "RIGHT_WRIST",
#     11: "LEFT_HIP",
#     12: "RIGHT_HIP",
#     13: "LEFT_KNEE",
#     14: "RIGHT_KNEE",
#     15: "LEFT_ANKLE",
#     16: "RIGHT_ANKLE",
# }

# class YOLOv8PoseWrapper:
#     def __init__(self, model="yolov8n-pose.pt", device=None, conf=0.3, imgsz=640):
#         if YOLO is None:
#             raise RuntimeError("ultralytics package not found. Install with `py -m pip install ultralytics`.")
#         # device: "cpu" or "cuda:0"
#         self.model = YOLO(model)
#         if device:
#             try:
#                 self.model.to(device)
#             except Exception:
#                 pass
#         self.conf = conf
#         self.imgsz = imgsz

#     def _extract_keypoints_from_result(self, res, frame_w, frame_h):
#         """
#         Attempt to find keypoints-like output inside the result object.
#         Different ultralytics versions expose different attributes.
#         We try a few likely ones and convert to a dict of normalized coords.
#         """
#         kps = None
#         # try common attribute names
#         if hasattr(res, "keypoints") and res.keypoints is not None:
#             kps = np.array(res.keypoints)  # expect shape (num_people, num_kpts, 3)
#         elif hasattr(res, "masks") and False:
#             # not a pose path, skip
#             kps = None
#         elif hasattr(res, "boxes") and hasattr(res.boxes, "keypoints"):
#             try:
#                 kps = np.array(res.boxes.keypoints)
#             except Exception:
#                 kps = None
#         elif hasattr(res, "keypoint") and res.keypoint is not None:
#             # some API variants
#             kps = np.array(res.keypoint)

#         # If kps is still None, try private attributes (best-effort)
#         if kps is None:
#             # try `res.xyxyn` or raw numpy arrays (some older versions)
#             try:
#                 if hasattr(res, "data") and len(res.data) > 0:
#                     arr = np.asarray(res.data)
#                     # not reliable; skip
#             except Exception:
#                 pass

#         # normalize and map to names; we only use the *first detected person* (typical webcam single person)
#         out = {}
#         if kps is not None and kps.size:
#             # If result has shape (N_people, N_kpts, 3) pick first
#             if kps.ndim == 3:
#                 kp = kps[0]
#             elif kps.ndim == 2 and kps.shape[0] >= 17:
#                 kp = kps  # assume it's already the kpt set
#             else:
#                 kp = kps.reshape(-1, 3)

#             # clamp and convert
#             for i in range(min(len(kp), 17)):
#                 x_px = float(kp[i, 0])
#                 y_px = float(kp[i, 1])
#                 conf = float(kp[i, 2]) if kp.shape[1] > 2 else 1.0
#                 # some outputs are normalized already (0..1). detect by scale.
#                 if x_px > 2.0 and frame_w > 0:
#                     x = x_px / float(frame_w)
#                     y = y_px / float(frame_h)
#                 else:
#                     x = x_px
#                     y = y_px
#                 # z is not available reliably from yolov8; use 0 and attach confidence in note if needed
#                 z = 0.0
#                 name = COCO17_IDX_TO_NAME.get(i, f"KP{i}")
#                 out[name] = (float(np.clip(x, 0.0, 1.0)), float(np.clip(y, 0.0, 1.0)), float(z))
#         return out

#     def findPose(self, frame, draw=False):
#         """
#         frame: BGR OpenCV frame (H,W,3)
#         returns: dict of keypoint_name -> (x_norm, y_norm, z)
#         """
#         h, w = frame.shape[:2]
#         # run model - ultralytics YOLO object supports callable semantics: self.model(frame, args...)
#         # the exact method signature depends on ultralytics version; using the call form is robust.
#         try:
#             results = self.model(frame, imgsz=self.imgsz, conf=self.conf)
#         except Exception as e:
#             # try legacy predict
#             results = self.model.predict(frame, imgsz=self.imgsz, conf=self.conf)

#         if not results:
#             return {}

#         # pick first result
#         res0 = results[0]
#         kp_dict = self._extract_keypoints_from_result(res0, w, h)
#         # optionally draw on frame
#         if draw and kp_dict:
#             # draw small dots for keypoints on the frame for debugging
#             for k, (x, y, z) in kp_dict.items():
#                 cv2.circle(frame, (int(x * w), int(y * h)), 3, (0, 255, 0), -1)
#         return kp_dict

# yolov8_adapter.py
"""
Adapter to run YOLOv8 pose models and return a mapping:
  NAME -> (x_norm, y_norm, z)
Uses ultralytics YOLO if available.
"""
import numpy as np
import cv2

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

# Extended COCO-style mapping (indices 0..16)
COCO17_IDX_TO_NAME = {
    0: "NOSE",
    1: "LEFT_EYE",
    2: "RIGHT_EYE",
    3: "LEFT_EAR",
    4: "RIGHT_EAR",
    5: "LEFT_SHOULDER",
    6: "RIGHT_SHOULDER",
    7: "LEFT_ELBOW",
    8: "RIGHT_ELBOW",
    9: "LEFT_WRIST",
    10: "RIGHT_WRIST",
    11: "LEFT_HIP",
    12: "RIGHT_HIP",
    13: "LEFT_KNEE",
    14: "RIGHT_KNEE",
    15: "LEFT_ANKLE",
    16: "RIGHT_ANKLE",
}

class YOLOv8PoseWrapper:
    def __init__(self, model="yolov8n-pose.pt", device=None, conf=0.25, imgsz=640):
        if YOLO is None:
            raise RuntimeError("ultralytics not found. Install via `pip install ultralytics`.")
        self.model = YOLO(model)
        if device:
            try:
                self.model.to(device)
            except Exception:
                pass
        self.conf = conf
        self.imgsz = imgsz

    def _parse_result_keypoints(self, res_item, frame_w, frame_h):
        """
        Try to extract keypoints from a result item (ultralytics result).
        Return dict name -> (x_norm,y_norm,z)
        """
        kps = None
        # Many ultralytics versions put keypoints in different places.
        # Try a safe, permissive set of accesses.
        try:
            # Some versions: res_item.keypoints -> shape (n_people, n_kpts, 3)
            if hasattr(res_item, "keypoints") and res_item.keypoints is not None:
                kps = np.asarray(res_item.keypoints)
            # Some versions embed in boxes.keypoints
            elif hasattr(res_item, "boxes") and hasattr(res_item.boxes, "keypoints"):
                try:
                    kps = np.asarray(res_item.boxes.keypoints)
                except Exception:
                    kps = None
            # Some legacy: res_item.keypoint
            elif hasattr(res_item, "keypoint") and res_item.keypoint is not None:
                kps = np.asarray(res_item.keypoint)
        except Exception:
            kps = None

        out = {}
        if kps is None or kps.size == 0:
            return out

        # If multiple people, use first.
        if kps.ndim == 3:
            kp0 = kps[0]
        elif kps.ndim == 2 and kps.shape[0] >= 17:
            kp0 = kps
        else:
            kp0 = kps.reshape(-1, kps.shape[-1])

        # Normalize coordinates to [0..1]. Some kps may already be normalized.
        for i in range(min(len(kp0), 17)):
            xi = float(kp0[i, 0])
            yi = float(kp0[i, 1])
            conf = float(kp0[i, 2]) if kp0.shape[1] > 2 else 1.0
            if frame_w > 0 and (xi > 2.0 or yi > 2.0):
                x = xi / float(frame_w)
                y = yi / float(frame_h)
            else:
                x = xi
                y = yi
            # clamp
            x = float(max(0.0, min(1.0, x)))
            y = float(max(0.0, min(1.0, y)))
            z = 0.0
            name = COCO17_IDX_TO_NAME.get(i, f"KP{i}")
            out[name] = (x, y, z)
        return out

    def findPose(self, frame, draw=False):
        """
        Run inference and return dict name -> (x_norm,y_norm,z).
        If draw=True, small markers are drawn on provided frame.
        """
        if frame is None:
            return {}
        h, w = frame.shape[:2]
        try:
            results = self.model(frame, imgsz=self.imgsz, conf=self.conf)
        except Exception:
            # fallback older API
            results = self.model.predict(frame, imgsz=self.imgsz, conf=self.conf)

        if not results or len(results) == 0:
            return {}

        res0 = results[0]
        kp_dict = self._parse_result_keypoints(res0, w, h)
        if draw and kp_dict:
            for k, (x, y, z) in kp_dict.items():
                cv2.circle(frame, (int(x * w), int(y * h)), 3, (0, 255, 0), -1)
        return kp_dict
