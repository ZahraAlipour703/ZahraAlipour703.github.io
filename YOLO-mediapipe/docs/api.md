# API reference (by class)

## `YOLODetector` — `src/detection/detector.py`
```python
YOLODetector(model_path: str, confidence: float = 0.35, device: str = "cpu")
detector.detect(frame: np.ndarray) -> list[Detection]
detector.draw(frame, detections) -> np.ndarray
detector.detect_and_draw(frame) -> np.ndarray
```
`Detection` fields: `bbox: list[int]`, `confidence: float`, `class_name: str = "hand"`.

## `MediaPipeTracker` — `src/tracking/mediapipe_tracker.py`
```python
MediaPipeTracker(static_image_mode=False, max_num_hands=1, detection_confidence=0.5, tracking_confidence=0.5)
tracker.process(frame, boxes: list[list[int]]) -> list[HandLandmarks]
tracker.draw(frame, hands) -> np.ndarray
tracker.close()
```
`HandLandmarks` fields: `bbox`, `landmarks: list[(x, y)]` (21 points, pixel space), `handedness: str`, `score: float`.

## `HandTracker` — `src/tracking/tracker.py`
```python
HandTracker(detector: YOLODetector, landmark_tracker: MediaPipeTracker, angle_calculator: AngleCalculator | None = None)
tracker.process(frame) -> TrackingResult
tracker.draw(result: TrackingResult) -> np.ndarray      # lightweight landmarks+FPS only
tracker.process_video(source=0)                          # standalone run loop, landmarks+FPS only
```
`TrackingResult` fields: `frame`, `detections: list[Detection]`, `hands: list[HandLandmarks]`, `angles: dict[str, float] | None`, `fps: float`.

## `AngleCalculator` — `src/geometry/angle_calculator.py`
```python
AngleCalculator.joint_angle(p1, p2, p3) -> float          # static, degrees
AngleCalculator.angle_between(v1, v2) -> float             # static, degrees
calculator.compute_from_landmarks(landmarks: list[tuple]) -> JointAngles
AngleCalculator.to_dictionary(joint_angles: JointAngles) -> dict
calculator.marker_angles(marker_dictionary, finger_layout) -> dict   # for ArUco-based angles
```

## `ArucoTracker` — `src/tracking/aruco_tracker.py`
```python
ArucoTracker(camera_matrix, distortion_coefficients, marker_length, dictionary=cv2.aruco.DICT_6X6_250)
tracker.detect(image) -> dict[int, MarkerPose]
tracker.draw(...)
```

## `Visualizer` — `src/visualization/visualization.py`
```python
visualizer.draw_pipeline(frame, detections, hands, poses, angles, fps, camera_matrix=None, distortion=None, marker_length=0.02, mask=None) -> np.ndarray
```
Also exposes each drawing step individually: `draw_yolo`, `draw_landmarks`, `draw_aruco`, `draw_angles`, `draw_fps`, `draw_mask`.

## `Config` / `cfg` — `src/utils/config.py`
```python
from src.utils.config import cfg
cfg.yolo_model, cfg.confidence, cfg.device
cfg.max_hands, cfg.detection_confidence, cfg.tracking_confidence
cfg.output_path, cfg.csv_path, cfg.video_output, cfg.image_output, cfg.log_output
cfg.draw_bbox, cfg.draw_landmarks, cfg.draw_angles, cfg.show_fps
cfg.save_video, cfg.save_csv, cfg.save_images
```
Backed by `config.yaml` at the repo root; required top-level sections: `paths`, `yolo`, `mediapipe`, `tracking`, `visualization`, `output`.
