# Installation

```bash
git clone https://github.com/ZahraAlipour703/YOLO-mediapipe.git
cd YOLO-mediapipe
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Model weights

`config.yaml`'s `yolo.model` / `paths.model` point at `models/yolov8n.pt` by
default. You don't need to place a file there yourself — passing a
recognized stock Ultralytics model name (like `yolov8n.pt`) to `YOLODetector`
triggers an automatic download on first use. To use your own fine-tuned hand
detector instead, put its `.pt` file at that path (or update `config.yaml`
to point elsewhere).

## Requirements

- Python 3.10+
- `ultralytics`
- `mediapipe`
- `opencv-python` + `opencv-contrib-python` (the latter for `cv2.aruco`)
- `numpy`
- `pyyaml`
- `scipy`

See `requirements.txt` for the full list.
