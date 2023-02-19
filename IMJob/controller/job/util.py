import time


class Timer:

    def __init__(self):
        self.elapsed = 0
        self.start = 0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed += (time.time() - self.start)


def convert_param(param: str, annotation):
    if annotation is int:
        try:
            return int(param), True
        except ValueError:
            return param, False

    elif annotation is float:
        try:
            return float(param), True
        except ValueError:
            return param, False

    elif (
        annotation is bool and
        param.lower() in ('true', 'false')
    ):
        return param.lower() == 'true', True

    return param, False


if __name__ == '__main__':
    param, ok = convert_param('1', int)
    print(param, ok)