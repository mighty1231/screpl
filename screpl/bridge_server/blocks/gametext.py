"""Defines GameTextBlock"""
from eudplib import *
from screpl.bridge_server import block

class GameTextBlock(block.BridgeBlock):
    """Provides game text

    .. code-block:: C

        struct GameTextBlock {
            int displayIndex;
            char display[13][218];
            char _unused[2]; // padding
        };
    """
    signature = b'TEXT'

    def get_buffer_size(self):
        return 4 + (13*218) + 2

    def update_content(self):
        f_dwwrite_epd(EPD(self), f_dwread_epd(EPD(0x640B58)))
        f_repmovsd_epd(EPD(self + 4), EPD(0x640B60), (13*218+2)//4)
