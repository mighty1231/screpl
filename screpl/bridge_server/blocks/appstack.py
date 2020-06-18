"""Defines AppStackBlock"""
from eudplib import *
from screpl.bridge_server import block

class AppStackBlock(block.BridgeBlock):
    """Prints app names on stack

    .. code-block:: C

        struct AppStackBlock {
            int stack_size;
            char names[2000]; // null-character separated strings
        };
    """
    signature = b'APST'

    def get_buffer_size(self):
        return 4 + 2000

    def update_content(self):
        from screpl.main import get_app_manager, get_main_writer
        SeqCompute([(EPD(self), SetTo, get_app_manager().app_stack.size)])
        get_main_writer().seekepd(EPD(self + 4))
        for app in get_app_manager().app_stack.values():
            get_main_writer().write_strepd(app.name_epd)
            get_main_writer().write(0)
