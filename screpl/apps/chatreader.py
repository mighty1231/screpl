"""defines ChatReaderApp"""
from eudplib import *

import screpl.core.application as application
import screpl.main as main
import screpl.utils.byterw as rw

_temp_storage = Db(220)
_temp_writer = rw.REPLByteRW()
_result_writer = rw.REPLByteRW()

class ChatReaderApp(application.Application):
    """Receives user's chat and write to specific offset

    Text UI:

    .. code-block:: text

        ChatReader
        Your input: '{Content}'

        [ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]

    Application usage to store text from user::

        my_database = Db(220)
        ChatReaderApp.set_return_epd(EPD(my_database))
        app_manager.start_application(ChatReaderApp)

        # Then, ChatReaderApp runs, and it stores text to my_database
    """

    @staticmethod
    def set_return_address(addr):
        """Set target address to store text from chat

        Call this before
        :meth:`~screpl.core.appmanager.AppManager.start_application`

        Args:
            addr(int, :class:`ConstExpr`, or :class:`EUDVariable`):
                target address
        """
        _result_writer.seekoffset(addr)

    @staticmethod
    def set_return_epd(epd):
        """Set epd value of target address to store text from chat

        Call this before
        :meth:`~screpl.core.appmanager.AppManager.start_application`

        Args:
            epd(int, :class:`ConstExpr`, or :class:`EUDVariable`):
                EPD value of target address
        """
        _result_writer.seekepd(epd)

    def on_init(self):
        """Initialize application

        It makes writer to focus return address
        """
        DoActions(SetMemoryX(_temp_storage, SetTo, 0, 0xFF))
        _temp_writer.seekepd(EPD(_temp_storage))
        _temp_writer.write_str(_result_writer.getoffset())
        _temp_writer.write(0)

    def on_destruct(self):
        _result_writer.seekepd(EPD(0))

    def on_chat(self, address):
        """Receives chat to store to temporary storage"""
        _temp_writer.seekepd(EPD(_temp_storage))
        _temp_writer.write_str(address)
        _temp_writer.write(0)
        main.get_app_manager().request_update()

    def loop(self):
        app_manager = main.get_app_manager()
        if EUDIf()([app_manager.key_press('Y', hold=['LCTRL'])]):
            _result_writer.write_strepd(EPD(_temp_storage))
            _result_writer.write(0)
            app_manager.request_destruct()
        if EUDElseIf()(app_manager.key_press('ESC')):
            app_manager.request_destruct()
        if EUDElseIf()([app_manager.key_press('N', hold=['LCTRL'])]):
            app_manager.request_destruct()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("\x13ChatReader\n")
        writer.write_f("\x13Your input: '%E'\n\n", EPD(_temp_storage))

        writer.write_f("\x13[ OK (CTRL+Y) ]    [ CANCEL (CTRL+N) ]\n")
        writer.write(0)
