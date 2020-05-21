'''
BlindModeDisplayBlock provides display for blindmode
'''
from eudplib import *
from .block import BridgeBlock
from ..core import getAppManager

appManager = getAppManager()
buffer_size = appManager.displayBuffer.GetDataSize()

class BlindModeDisplayBlock(BridgeBlock):
    signature = b'BLIN'

    def GetBufferSize(self):
        return buffer_size

    def UpdateContent(self):
        if EUDIf()(appManager.is_blind_mode == 1):
            f_repmovsd_epd(
                EPD(self),
                EPD(appManager.displayBuffer),
                buffer_size // 4
            )
        EUDEndIf()
