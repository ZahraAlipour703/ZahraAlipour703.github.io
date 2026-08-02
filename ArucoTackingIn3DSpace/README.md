# ArUco Cube Tracking in 3D Space

Real-time 3D position and orientation tracking of physical cubes using a webcam and ArUco fiducial markers — one marker per cube face — with a live local visualization overlay. No data is transmitted over a network; everything runs and displays locally.

## How It Works

1. **Camera capture & undistortion** — Frames are grabbed from the webcam and undistorted using the calibrated camera intrinsics/distortion coefficients.
2. **Marker detection** — OpenCV's ArUco module (`DICT_6X6_250`) detects visible markers and estimates each marker's pose.
3. **Marker → cube/face mapping** — Each marker ID maps to a `(cube_index, face_name)` pair.
4. **Per-face rotation correction** — A fixed correction rotation is applied per face so all detected faces agree on one consistent cube orientation.
5. **Multi-face averaging** — When multiple faces of a cube are visible, their positions are averaged and orientations combined via quaternion averaging.
6. **Temporal smoothing** — Position/orientation are smoothed over a rolling history to reduce jitter, with adaptive Z-depth smoothing and outlier rejection.
7. **Visualization** — A 3D wireframe cube, orientation arrows, and an info panel (position, quaternion, visible faces) are drawn per tracked cube.

## Project Structure

```
ArucoTrackingIn3DSpace/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── camera_calibration.yaml   # camera intrinsics, distortion, cm_to_pixel — per-camera
├── src/
│   └── cube_tracking/
│       ├── __init__.py
│       ├── config.py             # constants + calibration loading
│       ├── geometry.py           # marker/cube mapping, quaternion averaging
│       ├── smoothing.py          # CubeHistoryStore, temporal smoothing
│       ├── detection.py          # MarkerDetector: cv2.aruco wrapper
│       ├── visualization.py      # all cv2 drawing functions
│       └── app.py                # main loop: capture -> detect -> track -> draw
├── scripts/
│   └── run_tracking.py           # entry point
├── tools/
│   └── calibrate_camera.py       # generates config/camera_calibration.yaml
└── tests/
    ├── test_geometry.py
    └── test_smoothing.py
```

## Requirements

```bash
pip install -r requirements.txt
```

- Python 3.9+
- OpenCV with the `aruco` module (`opencv-contrib-python`)
- NumPy, SciPy, PyYAML

## Setup

1. **Calibrate your camera** (one-time, per camera):
   ```bash
   python tools/calibrate_camera.py --square-size-cm 2.5
   ```
   This writes `config/camera_calibration.yaml` with your camera's intrinsics and distortion coefficients. Follow the printed instructions to also fill in `cm_to_pixel` by measuring a known reference distance in a live frame.

2. **Attach ArUco markers** (`DICT_6X6_250`) to each of the 6 faces of every cube, using IDs `0..(NUM_CUBES * 6 - 1)` in the order `Top, Front, Back, Right, Left, Bottom` per cube.

3. **Adjust settings** in `src/cube_tracking/config.py` as needed (`NUM_CUBES`, `MARKER_SIZE_M`, smoothing constants, etc).

## Usage

```bash
python scripts/run_tracking.py
```

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Reset tracking history for all cubes |

## Running Tests

```bash
pytest tests/
```

## Notes

- This is a **local visualization tool only**. To forward tracking data elsewhere (another app, a robot, a game engine), add your own transmission layer (UDP, a message queue, a file interface, etc.) on top of `cube_tracking.app.process_frame`'s output.
- Camera calibration values and `cm_to_pixel` are specific to a given camera/lens/working-distance combination — recalibrate whenever any of those change.
