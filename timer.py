import time

class TimerError(Exception):
    """A custom exception that can be used to report errors
    in usage of the Timer class"""
class Timer:
    def __init__(self) -> None:
        self._start_time = None
    def start(self) -> None:
        if self._start_time is not None:
            raise TimerError(f"The timer is already running. Use .stop() to stop it.")
        self._start_time = time.perf_counter()
    def stop(self) -> float:
        if self._start_time is None:
            raise TimerError(f"The timer has not been started yet. Use .start() to start it.")
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return elapsed_time