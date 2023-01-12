import bson
import os
import threading
import time

class Storage:
    def __init__(self, filename, default_value):
        working_directory = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(working_directory, filename)
        self.default_value = default_value
        self.lock = threading.Lock()

        # Create file if it doesn't exist
        if not os.path.isfile(self.file_path):
            with open(self.file_path, "wb") as f:
                f.write(bson.dumps(self._wrap(default_value)))

    def _wrap(self, value):
        return { "state": value }

    def _unwrap(self, value):
        return value["state"]

    def get(self):
        with open(self.file_path, "rb") as f:
            data = f.read()
            if data:
                return self._unwrap(bson.loads(data))
            else:
                return self.default_value

    def set(self, value):
        with open(self.file_path, "wb") as f:
            f.write(bson.dumps(self._wrap(value)))
            
    def _check_file_change(self, callback):
        last_update_time = os.path.getmtime(self.file_path)
        while True:
            current_update_time = os.path.getmtime(self.file_path)
            if current_update_time != last_update_time:
                last_update_time = current_update_time
                with self.lock:
                    time.sleep(0.1)
                    callback(self.get())
