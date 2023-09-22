import logging
import time
_logger = logging.getLogger(__name__)

class Timer:
    def __init__(self, name: str):
        self.text = name
        self.start_time: float = 0.0
        self.end_time: float = 0.0

        self.entered = False

    def __enter__(self):
        self.entered = True
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.entered:
            raise Exception("How tf did this even happen")
        self.end_time = time.time()
        spent_time = self.end_time - self.start_time
        time_in_ms = spent_time * 1000.0
        _logger.info(f"{self.text}: {time_in_ms:.2f}ms")
