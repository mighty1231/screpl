'''
TUI
<no result>
 1. Results {""} not found, search string with chat.

<result>
 1. Search results "{string}", %D / Total %D found.
 2.  ##. {found line}
 3.  ##. {found line}
'''
from eudplib import *
from repl import Application

from . import appManager

MAX_SEARCH_CNT = 4096

# query statement, utf-8
db_target = Db(220)

# temporary buffer for search results, utf-8
db_search_buffer = Db(100000)

# search results
v_count = EUDVariable(0)
v_focused = EUDVariable(0) # searching_index
v_seached_strings = EUDArray(MAX_SEARCH_CNT) # searching_index

v_result_epd = EUDVariable(0)

class StringSearchApp(Application):
    @staticmethod
    def setResult_epd(result_epd):
        v_result_epd << result_epd

    def onDestruct(self):
        if EUDIf()([v_result_epd >= 1, v_count >= 1]):
            f_dwwrite_epd(v_result_epd, v_focused)
        EUDEndIf()
        v_result_epd << 0

    def onChat(self, offset):
        pass

    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        appManager.requestUpdate()

    def print(self, writer):
        if EUDIf()(v_count == 0):
            writer.write_f("Search results \"%E\" - not found\n")
        if EUDElse()():
            writer.write_f("Search results \"%E\" - %D / total %D found\n",
                v_focused,
                v_count)
        EUDEndIf()
        writer.write(0)
