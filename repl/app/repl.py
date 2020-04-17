from eudplib import *

from ..core.app import Application, getAppManager, AppCommand, runAppCommand
from ..utils import EPDConstStringArray, EUDByteRW
from .static import StaticApp

PAGE_NUMLINES = 8
LINESIZE = 216
REPLSIZE = 300

# REPL Should be guaranteed for exactly 1 instance
repl_input = Db(LINESIZE*REPLSIZE)
repl_output = Db(LINESIZE*REPLSIZE)
repl_inputEPDPtr = EUDVariable(EPD(repl_input))
repl_outputEPDPtr = EUDVariable(EPD(repl_output))
repl_index = EUDVariable() # increases for every I/O from 0

# Variables for current REPL page
repl_top_index = EUDVariable() # index of topmost at a page
repl_cur_page = EUDVariable()

repl_outputcolor = 0x16

writer = EUDByteRW()

class REPL(Application):
    def chatCallback(self, offset):
        writer.seekepd(repl_inputEPDPtr)
        writer.write_str(offset)
        writer.write(0)
        runAppCommand(
            offset,
            repl_outputEPDPtr
        )
        quot, mod = f_div(repl_index, PAGE_NUMLINES // 2)
        repl_top_index << repl_index - mod
        repl_cur_page << quot
        DoActions([
            repl_inputEPDPtr.AddNumber(LINESIZE // 4),
            repl_outputEPDPtr.AddNumber(LINESIZE // 4),
            repl_index.AddNumber(1)
        ])
        getAppManager().requestUpdate()

    def loop(self):
        # F7 - previous page
        # F8 - next page
        manager = getAppManager()
        if EUDIf()(manager.keyPress("F7")):
            if EUDIfNot()(repl_top_index == 0):
                DoActions([
                    repl_top_index.SubtractNumber( \
                            PAGE_NUMLINES//2),
                    repl_cur_page.SubtractNumber(1)
                ])
                manager.requestUpdate()
            EUDEndIf()
        if EUDElseIf()(manager.keyPress("F8")):
            if EUDIf()((repl_top_index+(PAGE_NUMLINES//2+1)). \
                        AtMost(repl_index)):
                DoActions([
                    repl_top_index.AddNumber( \
                            PAGE_NUMLINES//2),
                    repl_cur_page.AddNumber(1)
                ])
                manager.requestUpdate()
            EUDEndIf()
        EUDEndIf()

    def print(self, writer):
        # title
        cur_pn = repl_cur_page + 1
        if EUDIf()(repl_index == 0):
            cur_pn << 0
        EUDEndIf()

        writer.write_f("SC-REPL, type help() ( %D / %D )\n",
            cur_pn,
            f_div(repl_index + (PAGE_NUMLINES//2-1),
                PAGE_NUMLINES//2)[0]
        )

        # Write contents
        cur, inputepd, outputepd, until, pageend = EUDCreateVariables(5)
        cur << repl_top_index

        pageend << repl_top_index + PAGE_NUMLINES//2
        if EUDIf()(pageend >= repl_index):
            until << repl_index
        if EUDElse()():
            until << pageend
        EUDEndIf()

        off = (LINESIZE // 4) * cur
        inputepd << EPD(repl_input) + off
        outputepd << EPD(repl_output) + off
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            writer.write_f('\x1C>>> \x1D%E\n', inputepd)
            writer.write_f('%C%E\n', repl_outputcolor, outputepd)

            DoActions([
                cur.AddNumber(1),
                inputepd.AddNumber(LINESIZE // 4),
                outputepd.AddNumber(LINESIZE // 4),
            ])
        EUDEndInfLoop()

        # make empty lines
        if EUDInfLoop()():
            EUDBreakIf(cur >= pageend)
            writer.write(ord('\n'))
            writer.write(ord('\n'))
            DoActions(cur.AddNumber(1))
        EUDEndInfLoop()
        writer.write(0)

    @AppCommand([])
    def help(self):
        StaticApp.setContent(
            'SC-REPL manual',
            '\x13SC-REPL\n'
            + '\x13Made by sixthMeat\n'
            + '\n'
            + 'Key Inputs\n'
            + '- F7: Search previous page\n'
            + '- F8: Search next page\n'
            + '\n'
            + 'build in functions\n'
            + 'help() - See manual\n'
            + 'cmds() - See list of all commands\n'
        )
        getAppManager().openApplication(StaticApp)
