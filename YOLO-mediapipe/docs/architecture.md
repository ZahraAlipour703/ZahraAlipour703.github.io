# Architecture

## Pipeline

```
Video
  ↓
YOLO Detection            src.detection.detector.YOLODetector
  ↓
MediaPipe Hand Landmarks  src.tracking.mediapipe_tracker.MediaPipeTracker
  ↓
Joint Angle Calculation   src.geometry.angle_calculator.AngleCalculator
  ↓
Visualization             src.visualization.visualization.Visualizer
  ↓
Output Video + CSV
```

`src.tracking.tracker.HandTracker` orchestrates the first three stages: on
`process(frame)` it runs the YOLO detector to get hand bounding boxes, crops
each box and runs MediaPipe Hands inside it, then computes joint angles for
the first tracked hand. It returns a `TrackingResult` containing the raw
frame, YOLO `Detection`s, MediaPipe `HandLandmarks`, an angles dict, and the
current FPS.

`Visualizer.draw_pipeline(...)` takes a `TrackingResult`'s fields and draws
everything in one call: YOLO boxes, hand landmarks, joint angles, and FPS.

## Optional: ArUco + quaternion stage

`src.tracking.aruco_tracker.ArucoTracker` and `src.geometry.coordinate_system`
/ `src.geometry.quaternion` implement marker-based 6-DoF pose estimation and
quaternion math, for scenarios using physical ArUco markers instead of (or
alongside) MediaPipe landmarks. This stage is **not wired into `main.py` by
default** because it requires a real camera calibration
(`camera_matrix` + `distortion_coefficients`) that this project doesn't ship.
To enable it:

1. Calibrate your camera (OpenCV's standard checkerboard calibration
   produces `camera_matrix` and `distortion_coefficients`).
2. Construct `ArucoTracker(camera_matrix, distortion_coefficients, marker_length)`.
3. Call `.detect(frame)` each frame and pass `list(markers.values())` as
   `poses=` to `Visualizer.draw_pipeline`, along with the real
   `camera_matrix`/`distortion` arguments.

## Not currently wired in

`src.segmentation.segmentation.HandSegmenter` is fully implemented but not
called from `main.py`. `Visualizer.draw_mask()` already supports overlaying
a segmentation mask if you want to add this stage.

## Module map

| Module | Responsibility |
|---|---|
| `src/detection/detector.py` | `YOLODetector` — YOLO inference, `Detection` dataclass |
| `src/detection/train.py` / `evaluate.py` | Standalone YOLO training/evaluation, independent of the live pipeline |
| `src/tracking/mediapipe_tracker.py` | `MediaPipeTracker` — per-box MediaPipe Hands landmark extraction |
| `src/tracking/tracker.py` | `HandTracker` — orchestrates detector + landmark tracker + angle calculator |
| `src/tracking/aruco_tracker.py` | `ArucoTracker` — marker detection + pose/quaternion computation |
| `src/geometry/angle_calculator.py` | `AngleCalculator` — 3-point joint angles from landmarks; quaternion-based marker angles |
| `src/geometry/coordinate_system.py` | Rotation/transform matrix utilities |
| `src/geometry/quaternion.py` | `Quaternion` class and SLERP/averaging helpers |
| `src/preprocessing/preprocessing.py` | `FrameProcessor`, `VideoReader`, `VideoWriter` |
| `src/preprocessing/dataset.py` | `EgoHandsDataset` for training data |
| `src/preprocessing/augmentation.py` | `DataAugmentation` for training |
| `src/segmentation/segmentation.py` | `HandSegmenter` (not yet wired into `main.py`) |
| `src/utils/config.py` | `Config` class + `cfg` singleton, loaded from `config.yaml` |
| `src/utils/logger.py`, `utils.py` | Logging setup, general helper functions |
| `src/visualization/visualization.py` | `Visualizer` — all on-screen drawing |
