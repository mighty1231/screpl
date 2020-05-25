"""Defines AppOutputBlock"""
from eudplib import *
from screpl.bridge_server import block

APP_OUTPUT_MAXSIZE = 2000

appOutputSize = EUDVariable()
appOutputBuffer = Db(APP_OUTPUT_MAXSIZE)

class AppOutputBlock(block.BridgeBlock):
    """Provides utf-8 based text from applications

    .. code-block:: C

        struct AppOutputBlock {
            int app_output_sz;
            char app_output[2000];
        };
    """

    signature = b'AOUT'

    def get_buffer_size(self):
        return 4 + 2000

    def update_content(self):
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
