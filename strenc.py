# This library should be imported during *TriggerExec
# Otherwise, error happens - IndexError: list index out of range 

from eudplib import *
from encoder import ReadNumber, ReadString, ArgEncoderPtr
from table import ReferenceTable
from eudplib.core.rawtrigger.strdict import (
    DefUnitDict,
    DefAIScriptDict,
    DefLocationDict,
    DefSwitchDict,
)
from eudplib.core.mapdata.stringmap import (
    unitmap,
    locmap,
    swmap
)
from utils import *

tmpbuf = Db(150) # Temporarily store string
tmpstrbuf = DBString(150)

# @TODO : optimize for sub tables from location/switch
tbunit = ReferenceTable(unitmap._s2id.items(), "Unit")
tbunitsub = ReferenceTable(DefUnitDict.items(), "UnitSub")
tbloc = ReferenceTable(
    list(map(lambda a:(a[0], a[1]+1), locmap._s2id.items())), "Location")
tblocsub = ReferenceTable(DefLocationDict.items(), "LocationSub")
tbsw = ReferenceTable(swmap._s2id.items(), "Switch")
tbswsub = ReferenceTable(DefSwitchDict.items(), "SwitchSub")
tbai = ReferenceTable(
        list(map(lambda a:(a[0], b2i4(a[1])), DefAIScriptDict.items())), "AIScript")

@EUDFunc
def arg_EncodeUnit(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(tbunit.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        if EUDElseIf()(tbunitsub.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def arg_EncodeLocation(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(tbloc.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        if EUDElseIf()(tblocsub.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def arg_EncodeAIScript(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(tbai.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def arg_EncodeSwitch(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
        if EUDIf()(tbsw.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        if EUDElseIf()(tbswsub.search(tmpbuf, retval_epd) == 1):
            EUDReturn(1)
        EUDEndIf()
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

@EUDFunc
def arg_EncodeString(offset, delim, ref_offset_epd, retval_epd):
    if EUDIf()(ReadNumber(offset, delim, ref_offset_epd, retval_epd) == 1):
        EUDReturn(1)
    if EUDElseIf()(ReadString(offset, delim, ref_offset_epd, \
            EPD(tmpstrbuf.GetStringMemoryAddr())) == 1):
        sp = EUDVariable()
        strId = EncodeString("_" * 2048)
        if EUDExecuteOnce()():
            sp << GetMapStringAddr(strId)
        EUDEndExecuteOnce()
        f_strcpy(sp, tmpstrbuf.GetStringMemoryAddr())
        f_dwwrite_epd(retval_epd, strId)
        EUDReturn(1)
    EUDEndIf()
    f_dwwrite_epd(ref_offset_epd, offset)
    EUDReturn(0)

