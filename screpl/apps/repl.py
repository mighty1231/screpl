import inspect

from eudplib import *

import screpl.core.application as application
import screpl.core.appcommand as appcommand
import screpl.main as main
import screpl.utils.byterw as rw

from . import static
from . import logger

_PAGE_NUMLINES = 8
_LINE_SIZE = 216
_REPL_SIZE = 300

# Guarantee no more than 1 REPL instance
_repl_input = Db(_LINE_SIZE*_REPL_SIZE)
_repl_output = Db(_LINE_SIZE*_REPL_SIZE)
_repl_input_epd_ptr = EUDVariable(EPD(_repl_input))
_repl_output_epd_ptr = EUDVariable(EPD(_repl_output))
_repl_index = EUDVariable() # increases for every I/O from 0

# Variables for current REPL page
_repl_top_index = EUDVariable() # index of topmost at a page
_repl_cur_page = EUDVariable()

_repl_outputcolor = 0x16

class REPL(application.Application):
    _output_writer = rw.REPLByteRW()

    @staticmethod
    def get_output_writer():
        """returns writer object that supports to write output"""
        REPL._output_writer.seekepd(_repl_output_epd_ptr)
        return REPL._output_writer

    def on_chat(self, address):
        REPL._output_writer.seekepd(_repl_input_epd_ptr)
        REPL._output_writer.write_str(address)
        REPL._output_writer.write(0)

        application.Application.on_chat(self, address)

        quot, mod = f_div(_repl_index, _PAGE_NUMLINES // 2)
        _repl_top_index << _repl_index - mod
        _repl_cur_page << quot
        DoActions([
            _repl_input_epd_ptr.AddNumber(_LINE_SIZE // 4),
            _repl_output_epd_ptr.AddNumber(_LINE_SIZE // 4),
            _repl_index.AddNumber(1)
        ])
        main.get_app_manager().request_update()

    def loop(self):
        # F7 - previous page
        # F8 - next page
        manager = main.get_app_manager()
        if EUDIf()(manager.key_press("F7")):
            if EUDIfNot()(_repl_top_index == 0):
                DoActions([
                    _repl_top_index.SubtractNumber(_PAGE_NUMLINES//2),
                    _repl_cur_page.SubtractNumber(1)
                ])
                manager.request_update()
            EUDEndIf()
        if EUDElseIf()(manager.key_press("F8")):
            if EUDIf()((
                _repl_top_index+(_PAGE_NUMLINES//2+1)).AtMost(_repl_index)):
                DoActions([
                    _repl_top_index.AddNumber(_PAGE_NUMLINES//2),
                    _repl_cur_page.AddNumber(1),
                ])
                manager.request_update()
            EUDEndIf()
        EUDEndIf()

    def print(self, writer):
        # title
        cur_pn = _repl_cur_page + 1
        if EUDIf()(_repl_index == 0):
            cur_pn << 0
        EUDEndIf()

        writer.write_f("\x16SC-REPL, type help() ( %D / %D )\n",
            cur_pn,
            f_div(_repl_index + (_PAGE_NUMLINES//2-1),
                  _PAGE_NUMLINES//2)[0],
        )

        # Write contents
        cur, inputepd, outputepd, until, pageend = EUDCreateVariables(5)
        cur << _repl_top_index

        pageend << _repl_top_index + _PAGE_NUMLINES//2
        if EUDIf()(pageend >= _repl_index):
            until << _repl_index
        if EUDElse()():
            until << pageend
        EUDEndIf()

        off = (_LINE_SIZE // 4) * cur
        inputepd << EPD(_repl_input) + off
        outputepd << EPD(_repl_output) + off
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            writer.write_f("\x1C>>> \x1D%E\n", inputepd)
            writer.write_f("%C%E\n", _repl_outputcolor, outputepd)

            DoActions([
                cur.AddNumber(1),
                inputepd.AddNumber(_LINE_SIZE // 4),
                outputepd.AddNumber(_LINE_SIZE // 4),
            ])
        EUDEndInfLoop()

        writer.write(0)

    @appcommand.AppCommand([])
    def help(self):
        """Show manual of REPL"""
        static.StaticApp.set_content(
            "SC-REPL manual",
            "\x13SC-REPL\n"
            "\x13Made by sixthMeat (mighty1231@gmail.com)\n"
            "\n"
            "Key Inputs\n"
            "- F7: Search previous page\n"
            "- F8: Search next page\n"
            "\n"
            "builtin functions\n"
            "help() - Opens a manual\n"
            "cmds() - Shows registered commands\n"
        )
        main.get_app_manager().start_application(static.StaticApp)

    @appcommand.AppCommand([])
    def cmds(self):
        """Show REPL commands"""
        content = ''
        cmd_id = 1
        for name, cmd in REPL._commands_.ordered_items():
            argspec = inspect.getfullargspec(cmd.func)
            try:
                docstring = ': ' + cmd.func.__doc__.strip().split('\n')[0]
            except AttributeError:
                docstring = ''
            # encoders = cmd.arg_encoders

            arg_description = []
            for i in range(cmd.argn):
                arg_description.append('{}'.format(argspec.args[i+1]))
            content += '\x16{}. {}({}){}\n'.format(
                cmd_id,
                name,
                ', '.join(arg_description),
                docstring,
            )
            cmd_id += 1
        if content[-1] == '\n':
            content = content[:-1]

        static.StaticApp.set_content("\x16SC-REPL commands", content)
        main.get_app_manager().start_application(static.StaticApp)

    @appcommand.AppCommand([])
    def log(self):
        """Start Logger application"""
        main.get_app_manager().start_application(logger.Logger)
