import logging
import os
import sys


class Writer(object):
    def __init__(self, logger, pre=''):
        self.logger = logging.getLogger(logger)
        self.pre = pre
        self.buffer = ''

    def write(self, msg):
        if not msg:
            return
        if not self.buffer:
            self.buffer = self.pre + ': ' + msg
        else:
            self.buffer += msg
        if self.buffer.endswith('\n'):
            self.logger.info(self.buffer[:-1])
            self.buffer = ''

    def flush(self):
        if not self.buffer:
            return
        self.logger.info(self.buffer)
        self.buffer = ''


def get_call_file():
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back.f_back
    return f.f_code.co_filename


class CmdLoggerWriter(object):
    def __init__(self, logger):
        w = Writer(logger, os.path.basename(get_call_file()))
        sys.stdout = w
        sys.stderr = w

    def __call__(self, cls):
        return cls
