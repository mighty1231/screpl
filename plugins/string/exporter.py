from eudplib import *

from repl.core.application import Application

from . import *

STATE_CONFIG    = 0
STATE_EXPORTING = 1
v_state = EUDVariable(STATE_CONFIG)

MODE_SCMD      = 0
MODE_EUDPLIB   = 1
MODE_EUDEDITOR = 2
MODE_END     = 3
v_mode = EUDVariable(MODE_SCMD)

storage = Db(STRING_BUFFER_SZ)
remaining_bytes = EUDVariable(0)
written = EUDVariable(0)

def writeStrings():
    global string_buffer, new_alloc_epd, v_mode
    writer = app_manager.getWriter()
    writer.seekepd(EPD(storage))

    cur_epd = EUDVariable()
    cur_epd << EPD(string_buffer)

    # mode branch
    br_mode = Forward()
    br_mode_scmd = Forward()
    br_mode_eudplib = Forward()
    br_mode_eudeditor = Forward()
    br_mode_end = Forward()
    if EUDIf()(v_mode == MODE_SCMD):
        DoActions(SetNextPtr(br_mode, br_mode_scmd))
    if EUDElseIf()(v_mode == MODE_EUDPLIB):
        DoActions(SetNextPtr(br_mode, br_mode_eudplib))
    if EUDElseIf()(v_mode == MODE_EUDEDITOR):
        DoActions(SetNextPtr(br_mode, br_mode_eudeditor))
    EUDEndIf()

    if EUDInfLoop()():
        EUDBreakIf(cur_epd == new_alloc_epd)

        if EUDIf()(MemoryXEPD(cur_epd, Exactly, 0x0D0D0D, 0xFFFFFF)):
            b = f_bread_epd(cur_epd, 3)
            if EUDIf()(b <= 0x1F):
                if EUDIf()([b >= 9, b <= 10]): # \t and \n
                    writer.write(b)
                if EUDElse()():
                    br_mode << RawTrigger()

                    br_mode_scmd << NextTrigger()
                    writer.write(ord('<'))
                    writer.write_bytehex(b)
                    writer.write(ord('>'))
                    SetNextTrigger(br_mode_end)

                    br_mode_eudplib << NextTrigger()
                    writer.write_f("\\x")
                    writer.write_bytehex(b)
                    SetNextTrigger(br_mode_end)

                    br_mode_eudeditor << NextTrigger()
                    writer.write_f("<%D>", b)

                    br_mode_end << NextTrigger()
                EUDEndIf()
            if EUDElse()():
                writer.write(b)
            EUDEndIf()
        if EUDElseIf()(MemoryXEPD(cur_epd, Exactly, 0x0D0D, 0xFFFF)):
            b1 = f_bread_epd(cur_epd, 2)
            b2 = f_bread_epd(cur_epd, 3)
            writer.write(b1)
            writer.write(b2)
        if EUDElseIf()(MemoryXEPD(cur_epd, Exactly, 0x0D, 0xFF)):
            b1 = f_bread_epd(cur_epd, 1)
            b2 = f_bread_epd(cur_epd, 2)
            b3 = f_bread_epd(cur_epd, 3)
            writer.write(b1)
            writer.write(b2)
            writer.write(b3)
        if EUDElse()():
            # null-end
            writer.write_f("\n//------------//\n")
            if EUDInfLoop()():
                EUDBreakIf(cur_epd == new_alloc_epd)
                EUDBreakIf(MemoryEPD(cur_epd, AtLeast, 1))
                cur_epd += 1
            EUDEndInfLoop()
            EUDContinue()
        EUDEndIf()

        cur_epd += 1
    EUDEndInfLoop()
    writer.write(0)

    written << 0
    remaining_bytes << (writer.getoffset() - storage)

class StringExporterApp(Application):
    def onInit(self):
        pass

    def onDestruct(self):
        pass

    def loop(self):
        global written, remaining_bytes, v_mode

        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        EUDEndIf()

        if EUDIf()(v_state == STATE_CONFIG):
            if EUDIf()(app_manager.keyPress("Y", hold = ["LCTRL"])):
                v_state << STATE_EXPORTING
                writeStrings()
            if EUDElseIf()(app_manager.keyPress("O", hold = ["LCTRL"])):
                v_mode += 1
                Trigger(
                    conditions=v_mode.Exactly(MODE_END),
                    actions=v_mode.SetNumber(0)
                )
            EUDEndIf()
        if EUDElse()():
            new_written = app_manager.exportAppOutputToBridge(storage + written, remaining_bytes)

            remaining_bytes -= new_written
            written += new_written
            if EUDIf()(remaining_bytes == 0):
                v_state << STATE_CONFIG
            EUDEndIf()
        EUDEndIf()
        app_manager.requestUpdate()

    def print(self, writer):
        writer.write_f("String Editor - Exporter (Bridge Client required)\n")
        if EUDIf()(v_state == STATE_CONFIG):
            em_scmd, em_eudplib, em_eudeditor = EUDCreateVariables(3)
            if EUDIf()(v_mode == MODE_SCMD):
                DoActions([
                    em_scmd.SetNumber(0x11),
                    em_eudplib.SetNumber(0x16),
                    em_eudeditor.SetNumber(0x16)
                ])
            if EUDElseIf()(v_mode == MODE_EUDPLIB):
                DoActions([
                    em_scmd.SetNumber(0x16),
                    em_eudplib.SetNumber(0x11),
                    em_eudeditor.SetNumber(0x16)
                ])
            if EUDElse()():
                DoActions([
                    em_scmd.SetNumber(0x16),
                    em_eudplib.SetNumber(0x16),
                    em_eudeditor.SetNumber(0x11)
                ])
            EUDEndIf()
            writer.write_f("\n\x16Mode: %CSCMDraft2 %Ceudplib %CEUDEditor\n",
                em_scmd,
                em_eudplib,
                em_eudeditor)
            writer.write_f("\x16Press CTRL+O to change mode\n")
            writer.write_f("\x16Press CTRL+Y to export\n")
        if EUDElse()():
            writer.write_f("\x13Sent %D bytes / Remaining %D bytes\n\n\n\n",
                written,
                remaining_bytes
            )
        EUDEndIf()

        writer.write(0)
