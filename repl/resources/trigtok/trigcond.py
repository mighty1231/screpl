from eudplib import *
from ..table.tables import (
    tb_Modifier,
    tb_AllyStatus,
    tb_Comparison,
    tb_Order,
    tb_Player,
    tb_PropState,
    tb_Resource,
    tb_Score,
    tb_SwitchAction,
    tb_SwitchState,
)
from . import *

_condmap = EPDOffsetMap((
    ('locid', 0x00, 4),
    ('player', 0x04, 4),
    ('amount', 0x08, 4),
    ('unitid', 0x0C, 2),
    ('comparison', 0x0E, 1),
    ('condtype', 0x0F, 1),
    ('restype', 0x10, 1),
    ('flags', 0x11, 1),
    ('internal', 0x12, 2),
))

def encodeCondition_epd(condition_epd, cond):
    '''
     ======  =============  ========  ===========
     Offset  Field name     Position  EPD Player
     ======  =============  ========  ===========
       +00   locid           dword0   EPD(cond)+0
       +04   player          dword1   EPD(cond)+1
       +08   amount          dword2   EPD(cond)+2
       +0C   unitid          dword3   EPD(cond)+3
       +0E   comparison
       +0F   condtype
       +10   restype         dword4   EPD(cond)+4
       +11   flags
       +12   internal[2]
     ======  =============  ========  ===========
    '''
    assert isinstance(cond, Condition)

    f_dwwrite_epd(action_epd + 4, 0)

    if type(act.fields[0]) != int or act.fields[0] != 0:
        f_dwwrite_epd(action_epd, act.fields[0])
    if type(act.fields[1]) != int or act.fields[1] != 0:
        f_dwwrite_epd(action_epd + 1, act.fields[1])
    if type(act.fields[2]) != int or act.fields[2] != 0:
        f_dwwrite_epd(action_epd + 2, act.fields[2])
    if type(act.fields[3]) != int or act.fields[3] != 0:
        f_wwrite_epd(action_epd + 3, 0, act.fields[3])
    if type(act.fields[4]) != int or act.fields[4] != 0:
        f_bwrite_epd(action_epd + 3, 2, act.fields[4])
    if type(act.fields[5]) != int or act.fields[5] != 0:
        f_bwrite_epd(action_epd + 3, 3, act.fields[5])
    if type(act.fields[6]) != int or act.fields[6] != 0:
        f_bwrite_epd(action_epd + 4, 0, act.fields[6])
    if type(act.fields[7]) != int or act.fields[7] != 0:
        f_bwrite_epd(action_epd + 4, 1, act.fields[7])
    if type(act.fields[8]) != int or act.fields[8] != 0:
        f_wwrite_epd(action_epd + 4, 2, act.fields[8])

@EUDFunc
def writeCondition_epd(epd):
    conditions = EUDArray([
        0,
        EUDFuncPtr(1, 0)(_writeCountdownTimer),
        EUDFuncPtr(1, 0)(_writeCommand),
        EUDFuncPtr(1, 0)(_writeBring),
        EUDFuncPtr(1, 0)(_writeAccumulate),
        EUDFuncPtr(1, 0)(_writeKills),
        EUDFuncPtr(1, 0)(_writeCommandMost),
        EUDFuncPtr(1, 0)(_writeCommandMostAt),
        EUDFuncPtr(1, 0)(_writeMostKills),
        EUDFuncPtr(1, 0)(_writeHighestScore),
        EUDFuncPtr(1, 0)(_writeMostResources),
        EUDFuncPtr(1, 0)(_writeSwitch),
        EUDFuncPtr(1, 0)(_writeElapsedTime),
        EUDFuncPtr(1, 0)(_writeAlways), # Actually this should be Briefing()
        EUDFuncPtr(1, 0)(_writeOpponents),
        EUDFuncPtr(1, 0)(_writeDeaths),
        EUDFuncPtr(1, 0)(_writeCommandLeast),
        EUDFuncPtr(1, 0)(_writeCommandLeastAt),
        EUDFuncPtr(1, 0)(_writeLeastKills),
        EUDFuncPtr(1, 0)(_writeLowestScore),
        EUDFuncPtr(1, 0)(_writeLeastResources),
        EUDFuncPtr(1, 0)(_writeScore),
        EUDFuncPtr(1, 0)(_writeAlways),
        EUDFuncPtr(1, 0)(_writeNever),
    ])
    cond = _condmap(epd)
    condtype = cond.condtype
    if EUDIf()([condtype >= 1, condtype < 24]):
        EUDFuncPtr(1, 0).cast(conditions[condtype])(epd)
    if EUDElse()():
        getWriter().write_f("Condition(%D, %D, %D, %D, %D, %D, %D)",
            cond.locid,
            cond.player,
            cond.amount,
            cond.unitid,
            cond.comparison,
            condtype,
            cond.restype,
        )
    EUDEndIf()
    flags = cond.flags
    if EUDIf()(flags.ExactlyX(1, 1)):
        getWriter().write_f(' WaitExecute')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(2, 2)):
        getWriter().write_f(' IgnoreExecution')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(4, 4)):
        getWriter().write_f(' AlwaysDisplay')
    EUDEndIf()
    getWriter().write(0)

@EUDFunc
def _writeCountdownTimer(epd):
    m = _condmap(epd)
    getWriter().write_f("CountdownTimer(")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(")")


@EUDFunc
def _writeCommand(epd):
    m = _condmap(epd)
    getWriter().write_f("Command(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeBring(epd):
    m = _condmap(epd)
    getWriter().write_f("Bring(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    writeLocation(m.locid)
    getWriter().write_f(")")


@EUDFunc
def _writeAccumulate(epd):
    m = _condmap(epd)
    getWriter().write_f("Accumulate(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Resource), m.restype)
    getWriter().write_f(")")


@EUDFunc
def _writeKills(epd):
    m = _condmap(epd)
    getWriter().write_f("Kills(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(", ")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeCommandMost(epd):
    m = _condmap(epd)
    getWriter().write_f("CommandMost(")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeCommandMostAt(epd):
    m = _condmap(epd)
    getWriter().write_f("CommandMostAt(")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    writeLocation(m.locid)
    getWriter().write_f(")")


@EUDFunc
def _writeMostKills(epd):
    m = _condmap(epd)
    getWriter().write_f("MostKills(")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeHighestScore(epd):
    m = _condmap(epd)
    getWriter().write_f("HighestScore(")
    writeConstant(EPD(tb_Score), m.restype)
    getWriter().write_f(")")


@EUDFunc
def _writeMostResources(epd):
    m = _condmap(epd)
    getWriter().write_f("MostResources(")
    writeConstant(EPD(tb_Resource), m.restype)
    getWriter().write_f(")")


@EUDFunc
def _writeSwitch(epd):
    m = _condmap(epd)
    getWriter().write_f("Switch(")
    writeSwitch(m.restype)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_SwitchState), m.comparison)
    getWriter().write_f(")")


@EUDFunc
def _writeElapsedTime(epd):
    m = _condmap(epd)
    getWriter().write_f("ElapsedTime(")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(")")


@EUDFunc
def _writeOpponents(epd):
    m = _condmap(epd)
    getWriter().write_f("Opponents(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(")")


@EUDFunc
def _writeDeaths(epd):
    m = _condmap(epd)

    # consider EUD
    if EUDIf()(EUDOr(
            [m.player >= 27, m.unitid < 228],
            [m.player < 12, m.unitid >= 228],
            [m.internal == 0x4353])):
        # check EUDX
        if EUDIf()(m.internal == 0x4353): # eudx
            getWriter().write_f("MemoryX(%H, ",
                0x58A364 + 4*m.player + 48*m.unitid)
            writeConstant(EPD(tb_Comparison), m.comparison)
            getWriter().write_f(", %H(=%D), %H)", m.amount, m.amount, m.locid)
        if EUDElse()():
            getWriter().write_f("Memory(%H, ",
                0x58A364 + 4*m.player + 48*m.unitid)
            writeConstant(EPD(tb_Comparison), m.comparison)
            getWriter().write_f(", %H(=%D))", m.amount, m.amount)
        EUDEndIf()
    if EUDElse()():
        getWriter().write_f("Deaths(")
        writeConstant(EPD(tb_Player), m.player)
        getWriter().write_f(", ")
        writeConstant(EPD(tb_Comparison), m.comparison)
        getWriter().write_f(", ")
        getWriter().write_decimal(m.amount)
        getWriter().write_f(", ")
        writeUnit(m.unitid)
        getWriter().write_f(")")
    EUDEndIf()


@EUDFunc
def _writeCommandLeast(epd):
    m = _condmap(epd)
    getWriter().write_f("CommandLeast(")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeCommandLeastAt(epd):
    m = _condmap(epd)
    getWriter().write_f("CommandLeastAt(")
    writeUnit(m.unitid)
    getWriter().write_f(", ")
    writeLocation(m.locid)
    getWriter().write_f(")")


@EUDFunc
def _writeLeastKills(epd):
    m = _condmap(epd)
    getWriter().write_f("LeastKills(")
    writeUnit(m.unitid)
    getWriter().write_f(")")


@EUDFunc
def _writeLowestScore(epd):
    m = _condmap(epd)
    getWriter().write_f("LowestScore(")
    writeConstant(EPD(tb_Score), m.restype)
    getWriter().write_f(")")


@EUDFunc
def _writeLeastResources(epd):
    m = _condmap(epd)
    getWriter().write_f("LeastResources(")
    writeConstant(EPD(tb_Resource), m.restype)
    getWriter().write_f(")")


@EUDFunc
def _writeScore(epd):
    m = _condmap(epd)
    getWriter().write_f("Score(")
    writeConstant(EPD(tb_Player), m.player)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Score), m.restype)
    getWriter().write_f(", ")
    writeConstant(EPD(tb_Comparison), m.comparison)
    getWriter().write_f(", ")
    getWriter().write_decimal(m.amount)
    getWriter().write_f(")")


@EUDFunc
def _writeAlways(epd):
    getWriter().write_f("Always()")

@EUDFunc
def _writeNever(epd):
    getWriter().write_f("Never()")