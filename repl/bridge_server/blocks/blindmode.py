'''
BlindModeDisplayBlock provides display for blindmode
'''
from eudplib import *
from .block import BridgeBlock
from ..core import get_app_manager

app_manager = get_app_manager()
buffer_size = app_manager.displayBuffer.GetDataSize()

class BlindModeDisplayBlock(BridgeBlock):
    signature = b'BLIN'

    def GetBufferSize(self):
        return buffer_size

    def UpdateContent(self):
        if EUDIf()(app_manager.is_blind_mode == 1):
            f_repmovsd_epd(
                EPD(self),
                EPD(app_manager.displayBuffer),
                buffer_size // 4
            )
        EUDEndIf()
