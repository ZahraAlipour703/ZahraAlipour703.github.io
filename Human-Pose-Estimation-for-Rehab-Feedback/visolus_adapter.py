import os, sys, importlib, importlib.util, glob

def add_visolus_to_path(visolus_root=None):
    if visolus_root is None:
        visolus_root = os.path.join(os.path.dirname(__file__), "external", "Visolus")
    if os.path.isdir(visolus_root):
        if visolus_root not in sys.path:
            sys.path.insert(0, visolus_root)
    return visolus_root

def load_pose_wrapper(visolus_root=None):
    """
    Try to import a Pose wrapper from the Visolus subrepo.
    If found, return an instance exposing a method similar to: findPose(frame, draw=True) -> (img, landmarks)
    If not found, return None.
    """
    vis_root = add_visolus_to_path(visolus_root)
    # try common names
    candidates = [
        "pose_module", "src.pose_module", "visolus.pose_module",
        "pose", "src.pose"
    ]
    for name in candidates:
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "PoseModule"):
                try:
                    return mod.PoseModule()
                except Exception:
                    return mod
        except Exception:
            pass

    # try to find any python file containing "class .*Pose" or "def findPose"
    search = glob.glob(os.path.join(vis_root, "**", "*.py"), recursive=True)
    for p in search:
        try:
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            if "findPose" in txt or "PoseModule" in txt or "BlazePose" in txt:
                spec = importlib.util.spec_from_file_location("vis_mod", p)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "PoseModule"):
                    try:
                        return mod.PoseModule()
                    except Exception:
                        return mod
        except Exception:
            continue
    return None
