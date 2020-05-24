"""Defines BlindModeDisplayBlock"""
from eudplib import *
from screpl.bridge_server import block
import screpl.main as main

class BlindModeDisplayBlock(block.BridgeBlock):
    """Provides display for blind mode activated

    .. code-block:: C

        struct BlindModeDisplayBlock {
            char content[DISPLAY_BUFFER_SIZE];
        };
    """

    signature = b'BLIN'

    def get_buffer_size(self):
        buffer_size = main.get_app_manager().display_buffer.GetDataSize()
        return buffer_size

    def update_content(self):
        app_manager = main.get_app_manager()
        if EUDIf()(main.is_blind_mode()):
            f_repmovsd_epd(
                EPD(self),
                EPD(app_manager.display_buffer),
                self.get_buffer_size() // 4
            )
        EUDEndIf()
