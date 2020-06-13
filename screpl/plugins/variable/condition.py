from eudplib import *

from screpl.main import get_main_writer
from screpl.resources.table import tables as tb

writer = get_main_writer()

PLAYER_COLOR_CODES = [
    '\x08',
    '\x0e',
    '\x0f',
    '\x10',
    '\x11',
    '\x15',
    '\x16',
    '\x17',
]

class VariableConditionManager:
    def __init__(self):
        self.entries = []

        # prevent duplicates
        self.type_params = {}

    def add_entry(self, condition):
        condtype = condition[15]
        locid = b2i4(condition, 0)
        player = b2i4(condition, 4)
        unitid = b2i2(condition, 12)
        restype = b2i1(condition, 16)

        if condtype == 1:
            if condtype not in self.type_params:
                self.type_params[condtype] = True
                self.entries.append(_show_CountdownTimer)
        elif condtype == 2:
            params = self.type_params.get(condtype, [])
            if unitid not in params:
                params.append(unitid)
                self.type_params[condtype] = params
                self.entries.append(_make_show_Command(unitid))
        elif condtype == 3:
            params = self.type_params.get(condtype, [])
            if (unitid, locid) not in params:
                params.append((unitid, locid))
                self.type_params[condtype] = params
                self.entries.append(_make_show_Bring(unitid, locid))
        elif condtype == 4:
            params = self.type_params.get(condtype, [])
            if restype not in params:
                params.append(restype)
                self.type_params[condtype] = params
                self.entries.append(_make_show_Accumulate(restype))
        elif condtype == 5:
            params = self.type_params.get(condtype, [])
            if unitid not in params:
                params.append(unitid)
                self.type_params[condtype] = params
                self.entries.append(_make_show_Kills(unitid))
        elif condtype == 11:
            params = self.type_params.get(condtype, [])
            if restype not in params:
                self.type_params[condtype] = True
                self.entries.append(_make_show_Switch(restype))
        elif condtype == 12:
            if condtype not in self.type_params:
                self.type_params[condtype] = True
                self.entries.append(_show_ElapsedTime)
        elif condtype == 14:
            if condtype not in self.type_params:
                self.type_params[condtype] = True
                self.entries.append(_show_Opponents)
        elif condtype == 15:
            # prevent EUD
            params = self.type_params.get(condtype, [])
            if 0 <= player <= 26 and unitid not in params:
                params.append(unitid)
                self.type_params[condtype] = params
                self.entries.append(_make_show_Deaths(unitid))
        elif condtype == 21:
            params = self.type_params.get(condtype, [])
            if restype not in params:
                params.append(restype)
                self.type_params[condtype] = params
                self.entries.append(_make_show_Score(restype))

    def make_funcptrs(self):
        funcptrs = list(map(EUDFuncPtr(0, 0), self.entries))
        self.funcptr_arr = EUDArray(funcptrs)
        self.funcptr_len = len(funcptrs)

@EUDFunc
def _show_CountdownTimer():
    writer.write_f("\x16CountdownTimer %D",
                   EUDBinaryMax(lambda x:CountdownTimer(AtLeast, x)))

def _make_show_Command(unitid):
    @EUDFunc
    def _show_Command():
        values = [EUDBinaryMax(lambda x:Command(p, AtLeast, x, unitid))
                  for p in range(8)]
        writer.write_f("\x16Command ")
        writer.write_unit(unitid)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _show_Command

def _make_show_Bring(unitid, locid):
    @EUDFunc
    def _():
        values = [EUDBinaryMax(lambda x: Bring(p, AtLeast, x, unitid, locid))
                  for p in range(8)]
        writer.write_f("\x16Bring ")
        writer.write_unit(unitid)
        writer.write_f(" \x16in ")
        writer.write_location(locid)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _

def _make_show_Accumulate(restype):
    @EUDFunc
    def _():
        values = [EUDBinaryMax(lambda x: Accumulate(p, AtLeast, x, restype))
                  for p in range(8)]
        writer.write_f("\x16Accumulate ")
        writer.write_constant(EPD(tb.Resource), restype)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _

def _make_show_Kills(unitid):
    @EUDFunc
    def _():
        values = [EUDBinaryMax(lambda x: Kills(p, AtLeast, x, unitid))
                  for p in range(8)]
        writer.write_f("\x16Kills ")
        writer.write_unit(unitid)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _

def _make_show_Switch(swid):
    @EUDFunc
    def _():
        writer.write_f("\x16Switch %E ", tb.get_switchname_epd(swid))
        if EUDIf()(Switch(swid, Set)):
            writer.write_f("\x07Set")
        if EUDElse()():
            writer.write_f("\x06Cleared")
        EUDEndIf()
    return _

@EUDFunc
def _show_ElapsedTime():
    writer.write_f("\x16ElapsedTime %D",
                   EUDBinaryMax(lambda x:ElapsedTime(AtLeast, x)))

@EUDFunc
def _show_Opponents():
    values = [EUDBinaryMax(lambda x: Opponents(p, AtLeast, x))
              for p in range(8)]
    writer.write_f("\x16Opponents ")
    writer.write_f(
        " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
        PLAYER_COLOR_CODES[0], values[0],
        PLAYER_COLOR_CODES[1], values[1],
        PLAYER_COLOR_CODES[2], values[2],
        PLAYER_COLOR_CODES[3], values[3],
        PLAYER_COLOR_CODES[4], values[4],
        PLAYER_COLOR_CODES[5], values[5],
        PLAYER_COLOR_CODES[6], values[6],
        PLAYER_COLOR_CODES[7], values[7],
    )

def _make_show_Deaths(unitid):
    @EUDFunc
    def _():
        values = [f_dwread_epd(12*unitid + p) for p in range(8)]
        writer.write_f("\x16Deaths ")
        writer.write_unit(unitid)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _

def _make_show_Score(restype):
    @EUDFunc
    def _():
        values = [EUDBinaryMax(lambda x: Score(p, restype, AtLeast, x))
                  for p in range(8)]
        writer.write_f("\x16Score ")
        writer.write_constant(EPD(tb.Score), restype)
        writer.write_f(
            " %S%D %S%D %S%D %S%D %S%D %S%D %S%D %S%D",
            PLAYER_COLOR_CODES[0], values[0],
            PLAYER_COLOR_CODES[1], values[1],
            PLAYER_COLOR_CODES[2], values[2],
            PLAYER_COLOR_CODES[3], values[3],
            PLAYER_COLOR_CODES[4], values[4],
            PLAYER_COLOR_CODES[5], values[5],
            PLAYER_COLOR_CODES[6], values[6],
            PLAYER_COLOR_CODES[7], values[7],
        )
    return _

