"""Add methods on REPLByteRW to write trigger conditions"""

from eudplib import *
from screpl.resources.table import tables as tb

def writer_condition_init():
    """Add a method on REPLByteRW"""
    from screpl.utils.byterw import REPLByteRW

    REPLByteRW.add_method(write_condition_epd)

condition_epd_offset_map = EPDOffsetMap((
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

@EUDMethod
def write_condition_epd(self, epd):
    """Write trigger condition with eudplib syntax"""

    # condtype 13 should be Briefing() but it has same
    # semantics with Always()
    write_mtds = [
        (1, _write__CountdownTimer),
        (2, _write__Command),
        (3, _write__Bring),
        (4, _write__Accumulate),
        (5, _write__Kills),
        (6, _write__CommandMost),
        (7, _write__CommandMostAt),
        (8, _write__MostKills),
        (9, _write__HighestScore),
        (10, _write__MostResources),
        (11, _write__Switch),
        (12, _write__ElapsedTime),
        (13, _write__Always),
        (14, _write__Opponents),
        (15, _write__Deaths),
        (16, _write__CommandLeast),
        (17, _write__CommandLeastAt),
        (18, _write__LeastKills),
        (19, _write__LowestScore),
        (20, _write__LeastResources),
        (21, _write__Score),
        (22, _write__Always),
        (23, _write__Never)]

    cond = condition_epd_offset_map(epd)
    condtype = cond.condtype
    for mtd_id, mtd in write_mtds:
        _br = EUDIf if mtd_id == 1 else EUDElseIf
        _br()(condtype == mtd_id)
        mtd(self, epd)
    if EUDElse()():
        self.write_f(
            "Condition(%D, %D, %D, %D, %D, %D, %D)",
            cond.locid,
            cond.player,
            cond.amount,
            cond.unitid,
            cond.comparison,
            condtype,
            cond.restype,
        )
    EUDEndIf()

    # additional flags
    flags = cond.flags
    if EUDIf()(flags.ExactlyX(1, 1)):
        self.write_f(' WaitExecute')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(2, 2)):
        self.write_f(' IgnoreExecution')
    EUDEndIf()
    if EUDIf()(flags.ExactlyX(4, 4)):
        self.write_f(' AlwaysDisplay')
    EUDEndIf()

@EUDMethod
def _write__CountdownTimer(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("CountdownTimer(")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(")")


@EUDMethod
def _write__Command(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Command(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__Bring(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Bring(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid)
    self.write_f(")")


@EUDMethod
def _write__Accumulate(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Accumulate(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_constant(EPD(tb.Resource), m.restype)
    self.write_f(")")


@EUDMethod
def _write__Kills(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Kills(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(", ")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__CommandMost(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("CommandMost(")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__CommandMostAt(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("CommandMostAt(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid)
    self.write_f(")")


@EUDMethod
def _write__MostKills(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("MostKills(")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__HighestScore(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("HighestScore(")
    self.write_constant(EPD(tb.Score), m.restype)
    self.write_f(")")


@EUDMethod
def _write__MostResources(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("MostResources(")
    self.write_constant(EPD(tb.Resource), m.restype)
    self.write_f(")")


@EUDMethod
def _write__Switch(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Switch(")
    self.write_switch(m.restype)
    self.write_f(", ")
    self.write_constant(EPD(tb.SwitchState), m.comparison)
    self.write_f(")")


@EUDMethod
def _write__ElapsedTime(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("ElapsedTime(")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(")")


@EUDMethod
def _write__Opponents(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Opponents(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(")")


@EUDMethod
def _write__Deaths(self, epd):
    m = condition_epd_offset_map(epd)

    # consider EUD
    if EUDIf()(EUDOr([m.player >= 27, m.unitid < 228],
                     [m.player < 12, m.unitid >= 228],
                     [m.internal == 0x4353])):
        # check EUDX
        if EUDIf()(m.internal == 0x4353): # eudx
            self.write_f("MemoryX(%H, ",
                         0x58A364 + 4*m.player + 48*m.unitid)
            self.write_constant(EPD(tb.Comparison), m.comparison)
            self.write_f(", %H(=%D), %H)", m.amount, m.amount, m.locid)
        if EUDElse()():
            self.write_f("Memory(%H, ",
                         0x58A364 + 4*m.player + 48*m.unitid)
            self.write_constant(EPD(tb.Comparison), m.comparison)
            self.write_f(", %H(=%D))", m.amount, m.amount)
        EUDEndIf()
    if EUDElse()():
        self.write_f("Deaths(")
        self.write_constant(EPD(tb.Player), m.player)
        self.write_f(", ")
        self.write_constant(EPD(tb.Comparison), m.comparison)
        self.write_f(", ")
        self.write_decimal(m.amount)
        self.write_f(", ")
        self.write_unit(m.unitid)
        self.write_f(")")
    EUDEndIf()


@EUDMethod
def _write__CommandLeast(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("CommandLeast(")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__CommandLeastAt(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("CommandLeastAt(")
    self.write_unit(m.unitid)
    self.write_f(", ")
    self.write_location(m.locid)
    self.write_f(")")


@EUDMethod
def _write__LeastKills(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("LeastKills(")
    self.write_unit(m.unitid)
    self.write_f(")")


@EUDMethod
def _write__LowestScore(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("LowestScore(")
    self.write_constant(EPD(tb.Score), m.restype)
    self.write_f(")")


@EUDMethod
def _write__LeastResources(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("LeastResources(")
    self.write_constant(EPD(tb.Resource), m.restype)
    self.write_f(")")


@EUDMethod
def _write__Score(self, epd):
    m = condition_epd_offset_map(epd)
    self.write_f("Score(")
    self.write_constant(EPD(tb.Player), m.player)
    self.write_f(", ")
    self.write_constant(EPD(tb.Score), m.restype)
    self.write_f(", ")
    self.write_constant(EPD(tb.Comparison), m.comparison)
    self.write_f(", ")
    self.write_decimal(m.amount)
    self.write_f(")")


@EUDMethod
def _write__Always(self, epd):
    self.write_f("Always()")

@EUDMethod
def _write__Never(self, epd):
    self.write_f("Never()")
