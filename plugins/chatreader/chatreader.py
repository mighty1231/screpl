'''
ChatReader
You input '{Content}'

[ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]
'''

from eudplib import *
from repl import (
    Application,
    getAppManager,
    EUDByteRW
)

appManager = getAppManager()

temp_storage = Db(220)
temp_writer = EUDByteRW()

result_writer = EUDByteRW()

class ChatReaderApp(Application):
    @staticmethod
    def setResult_offset(result_offset):
        result_writer.seekoffset(result_offset)

    @staticmethod
    def setResult_epd(result_epd):
        result_writer.seekepd(result_epd)

    def onInit(self):
        DoActions(SetMemoryX(temp_storage, SetTo, 0, 0xFF))

    def onDestruct(self):
        result_writer.seekepd(EPD(0))

    def onChat(self, offset):
        temp_writer.seekepd(EPD(temp_storage))
        temp_writer.write_str(offset)
        temp_writer.write(0)
        appManager.requestUpdate()

    def loop(self):
        if EUDIf()([appManager.keyPress('Y', hold=['LCTRL'])]):
            result_writer.write_strepd(EPD(temp_storage))
            result_writer.write(0)
            appManager.requestDestruct()
        if EUDElseIf()(appManager.keyPress('ESC')):
            appManager.requestDestruct()
        if EUDElseIf()([appManager.keyPress('N', hold=['LCTRL'])]):
            appManager.requestDestruct()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x13ChatReader\n")
        writer.write_f("\x13Your input: '%E'\n\n", EPD(temp_storage))

        writer.write_f("\x13[ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]\n")
        writer.write(0)
