# progress_tracker.py

import os
import json

class ProgressTracker:
    def __init__(self, file_path="progress.json"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)

    def get_progress(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def update_progress(self, topic: str):
        """
        Marks the given topic as completed.
        :param topic: str - The topic or concept name
        :return: Updated progress as a JSON string
        """
        data = self.get_progress()
        data[topic] = "Completed "
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)
        return json.dumps(data, indent=2)
