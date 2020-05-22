'''
BlindModeDisplayBlock provides display for blindmode
'''
from eudplib import *
from repl.bridge_server import block
import repl.main as main

class BlindModeDisplayBlock(block.BridgeBlock):
    signature = b'BLIN'

    def GetBufferSize(self):
        buffer_size = main.get_app_manager().display_buffer.GetDataSize()
        return buffer_size

    def UpdateContent(self):
        app_manager = main.get_app_manager()
        if EUDIf()(app_manager.is_blind_mode == 1):
            f_repmovsd_epd(
                EPD(self),
                EPD(app_manager.display_buffer),
                self.GetBufferSize() // 4
            )
        EUDEndIf()
