'''
ChatReader
You input '{Content}'

[ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]
'''

from eudplib import *
from repl import (
    Application,
    get_app_manager,
    EUDByteRW
)

temp_storage = Db(220)
temp_writer = EUDByteRW()

result_writer = EUDByteRW()

class ChatReaderApp(Application):
    @staticmethod
    def setResult_offset(result_offset):
        result_writer.seekoffset(result_offset)

    @staticmethod
    def set_return_epd(result_epd):
        result_writer.seekepd(result_epd)

    def onInit(self):
        DoActions(SetMemoryX(temp_storage, SetTo, 0, 0xFF))
        temp_writer.seekepd(EPD(temp_storage))
        temp_writer.write_str(result_writer.getoffset())
        temp_writer.write(0)

    def onDestruct(self):
        result_writer.seekepd(EPD(0))

    def onChat(self, offset):
        temp_writer.seekepd(EPD(temp_storage))
        temp_writer.write_str(offset)
        temp_writer.write(0)
        get_app_manager().requestUpdate()

    def loop(self):
        app_manager = get_app_manager()
        if EUDIf()([app_manager.keyPress('Y', hold=['LCTRL'])]):
            result_writer.write_strepd(EPD(temp_storage))
            result_writer.write(0)
            app_manager.requestDestruct()
        if EUDElseIf()(app_manager.keyPress('ESC')):
            app_manager.requestDestruct()
        if EUDElseIf()([app_manager.keyPress('N', hold=['LCTRL'])]):
            app_manager.requestDestruct()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x13ChatReader\n")
        writer.write_f("\x13Your input: '%E'\n\n", EPD(temp_storage))

        writer.write_f("\x13[ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]\n")
        writer.write(0)
