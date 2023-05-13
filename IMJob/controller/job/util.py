import time
from typing import Any


class Timer:

    def __init__(self, enabled: bool = True):
        self.elapsed = 0
        self.start = 0
        self.enabled = enabled

    def __enter__(self):
        if self.enabled:
            self.start = time.time()
        return self

    def __exit__(self, *args):
        if self.enabled:
            self.elapsed += (time.time() - self.start)


def convert_param(param: str, annotation: Any):
    try:
        return annotation(param), True
    except (TypeError, ValueError):
        return param, False


if __name__ == '__main__':
    pass
