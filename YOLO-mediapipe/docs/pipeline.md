# Pipeline walkthrough

This walks through exactly what happens for one frame when you run
`python main.py --source 0`.

1. **`VideoReader.frames()`** yields the next BGR frame from the camera/video.
2. **`HandTracker.process(frame)`**:
   - `YOLODetector.detect(frame)` runs YOLO inference and returns a list of
     `Detection(bbox, confidence, class_name)`.
   - For each detection's `bbox`, `MediaPipeTracker.process(frame, boxes)`
     crops that region and runs MediaPipe Hands on the crop, returning a
     `HandLandmarks(bbox, landmarks, handedness, score)` per detected hand
     (landmarks are 21 `(x, y)` pixel points, already offset back into the
     full frame's coordinate space).
   - If any hand was found, `AngleCalculator.compute_from_landmarks(hands[0].landmarks)`
     computes a `JointAngles` dataclass (wrist + 3 joints per finger), which
     is converted to a flat dict via `AngleCalculator.to_dictionary(...)`.
   - All of this is packaged into a `TrackingResult(frame, detections, hands, angles, fps)`.
3. **`Visualizer.draw_pipeline(...)`** draws, in order: YOLO boxes
   (`draw_yolo`), hand landmarks (`draw_landmarks`), ArUco markers if a
   camera calibration was supplied (`draw_aruco`), joint angles
   (`draw_angles`), FPS (`draw_fps`), and a segmentation mask if one was
   supplied (`draw_mask`).
4. The annotated frame is shown in a window and, with `--save`, written to
   `outputs/videos/output.mp4` via `VideoWriter`.
5. Press `q` to stop. `VideoReader.release()` and `MediaPipeTracker.close()`
   are called on exit.

## Where CSV logging fits in

`Config.save_csv` / `cfg.csv_path` are already resolved by `Config`, but
`main.py` does not currently write per-frame angle data to CSV — this is
the most natural next feature to add: append `result.angles` (with a
timestamp) to `cfg.csv_path` each frame when `cfg.save_csv` is true, similar
to the session logging pattern used in the [Human-Pose-Estimation-for-Rehab-Feedback](https://github.com/ZahraAlipour703/Human-Pose-Estimation-for-Rehab-Feedback)
project.
