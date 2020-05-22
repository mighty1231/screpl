'''
GameTextBlock provides game text

struct {
    int displayIndex;
    char display[13][218];
    char _unused[2]; # padding
}
'''
from eudplib import *
from screpl.bridge_server import block

class GameTextBlock(block.BridgeBlock):
    signature = b'TEXT'

    def GetBufferSize(self):
        return 4 + (13*218) + 2

    def UpdateContent(self):
        f_dwwrite_epd(EPD(self), f_dwread_epd(EPD(0x640B58)))
        f_repmovsd_epd(EPD(self + 4), EPD(0x640B60), (13*218+2)//4)
