'''
AppOutputBlock provides game text

struct {
    int app_output_sz;
    char app_output[2000];
}
'''
from eudplib import *
from repl.bridge_server import block

APP_OUTPUT_MAXSIZE = 2000

appOutputSize = EUDVariable()
appOutputBuffer = Db(APP_OUTPUT_MAXSIZE)

class AppOutputBlock(block.BridgeBlock):
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
