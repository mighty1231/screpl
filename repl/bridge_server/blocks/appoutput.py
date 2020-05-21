'''
AppOutputBlock provides game text

struct {
    int app_output_sz;
    char app_output[2000];
}
'''
from eudplib import *
from .block import BridgeBlock
from ..core import get_app_manager

APP_OUTPUT_MAXSIZE = 2000
app_manager = get_app_manager()

appOutputSize = EUDVariable()
appOutputBuffer = Db(APP_OUTPUT_MAXSIZE)

class AppOutputBlock(BridgeBlock):
    signature = b'AOUT'

    def GetBufferSize(self):
        return 4 + 2000

    def UpdateContent(self):
        # Check for flushed to client
        if EUDIf()(Memory(self, Exactly, 0)):
            SeqCompute([(EPD(self), SetTo, appOutputSize)])
            f_repmovsd_epd(
                EPD(self + 4),
                EPD(appOutputBuffer),
                APP_OUTPUT_MAXSIZE//4
            )

            # Notify buffer is flushed
            appOutputSize << 0
        EUDEndIf()
