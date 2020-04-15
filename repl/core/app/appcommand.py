from eudplib import *

class AppCommand:
    def __init__(self, func):
        self.cls = None
        self.func = func

    def setClass(self, cls):
        self.cls = cls

    def __call__(self, *args, **kwargs):
        # use EUDCommand
        # @TODO
        return self.func(self.cls, *args, **kwargs)

