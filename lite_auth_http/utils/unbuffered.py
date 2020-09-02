import sys


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def unbuffered(func):
    def inner(*args, **kwargs):
        sys.stdout = Unbuffered(sys.stdout)
        return func(*args, **kwargs)
    return inner
