import time, json, os

class BaseExerciseChecker:
    def __init__(self, name, config, logger=None):
        self.name = name
        self.config = config
        self.logger = logger
        self.state = "idle"
        self.events = []
    def update(self, landmarks, t=None):
        raise NotImplementedError
    def log(self, metric, value, note=""):
        entry = {"time": time.time(), "exercise": self.name, "metric": metric, "value": value, "note": note}
        self.events.append(entry)
        if self.logger:
            try:
                self.logger.writerow([entry["time"], entry["exercise"], entry["metric"], entry["value"], entry["note"]])
            except Exception:
                pass
    def save_session(self, filename):
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2)
