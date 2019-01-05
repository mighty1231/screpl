from eudplib import *
from .view import _view_writer, EUDView, dbpool, varpool
from .static import StaticView
from ..utils import makeEPDText, f_strcmp_ptrepd
from ..core.table import SearchTableInv
from ..core.encoder import ReadName, ReadNumber
from ..resources.table.tables import tb_unit, tb_unitMap

LINESIZE = 216
PAGE_NUMCONTENTS = 8

class UnitArrayViewMembers(EUDStruct):
	_fields_ = [
		# buffer for current screen
		'screen_data_epd',

		# state variables
		'offset', # 0 ~ 1699 -> 0x59CCA8 + 336*i
		'unitptr', # 0x59CCA8 + 336*i
		'unitepd', # EPD(0x59CCA8 + 336*i)
	]

varn = len(UnitArrayViewMembers._fields_)

@EUDFunc
def unitarrayview_init(unused):
	members = UnitArrayViewMembers.cast(varpool.alloc(varn))
	members.screen_data_epd = dbpool.alloc_epd( \
		LINESIZE * (PAGE_NUMCONTENTS + 1))

	members.offset = 0
	members.unitptr = 0x59CCA8
	members.unitepd = EPD(0x59CCA8)

	EUDReturn(members)

@EUDTypedFunc([UnitArrayViewMembers, None])
def unitarrayview_keydown_callback(members, keycode):
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7 - Prev Page
		if EUDIf()(members.offset >= PAGE_NUMCONTENTS):
			members.offset -= PAGE_NUMCONTENTS
			members.unitptr -= 336 * PAGE_NUMCONTENTS
			members.unitepd -= (336//4) * PAGE_NUMCONTENTS
		if EUDElse()():
			members.offset = 0
			members.unitptr = 0x59CCA8
			members.unitepd = EPD(0x59CCA8)
		EUDEndIf()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8 - Next Page
		if EUDIf()(members.offset <= 1699 - PAGE_NUMCONTENTS):
			members.offset += PAGE_NUMCONTENTS
			members.unitptr += 336 * PAGE_NUMCONTENTS
			members.unitepd += (336//4) * PAGE_NUMCONTENTS
		if EUDElse()():
			members.offset = 1699
			members.unitptr = 0x59CCA8 + 336*1699
			members.unitepd = EPD(0x59CCA8 + 336*1699)
		EUDEndIf()
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([UnitArrayViewMembers, None])
def unitarrayview_execute_chat(members, offset):
	# help -> open view for help
	# (number) -> set index to it (offset = 0 if index = 0 else 1700 - index)
	new_idx = EUDVariable()
	if EUDIf()(ReadNumber(offset, 0, EPD(offset.getValueAddr()), \
			EPD(new_idx.getValueAddr())) == 1):
		if EUDIf()([new_idx >= 1, new_idx < 1700]):
			members.offset = 1700 - new_idx
			members.unitptr = 0x59CCA8 + 336 * members.offset
			members.unitepd = EPD(0x59CCA8) + (336//4) * members.offset
		if EUDElseIf()(new_idx == 0):
			members.offset = 0
			members.unitptr = 0x59CCA8
			members.unitepd = EPD(0x59CCA8)
		EUDEndIf()
		EUDReturn(1)
	if EUDElseIf()(f_strcmp_ptrepd(offset, makeEPDText("?")) == 0):
		args = EUDArray([
			makeEPDText("UNITARRAY VIEW"),
			7,
			makeEPDText("Keycode"),
			makeEPDText("F7: Go to left page"),
			makeEPDText("F8: Go to right page"),
			makeEPDText(""),
			makeEPDText("Type"),
			makeEPDText("?: get help"),
			makeEPDText("(number): go to index"),
		])
		StaticView.OpenView(EPD(args))
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_loop(members):
	# title line
	off, ptr, epd = members.offset, members.unitptr, members.unitepd

	_view_writer.seekepd(members.screen_data_epd)
	_view_writer.write_strepd(makeEPDText('CUnit-array View, type "?" for help, offset = '))
	_view_writer.write_decimal(off)
	_view_writer.write_strepd(makeEPDText(' (0 ~ 1699)\n'))

	until = EUDVariable()
	pageend = off + PAGE_NUMCONTENTS
	if EUDIf()(pageend >= 1700):
		until << 1700
	if EUDElse()():
		until << pageend
	EUDEndIf()

	if EUDInfLoop()():
		EUDBreakIf(off >= until)
		_view_writer.write(0x16)
		_view_writer.write_hex(ptr)

		# print sprite pointer
		spriteptr = f_dwread_epd(epd + (0x0C // 4))
		if EUDIf()(spriteptr == 0):
			_view_writer.write_strepd(makeEPDText(\
					': (Spriteptr = \x060x00000000\x16'))
		if EUDElse()():
			_view_writer.write_strepd(makeEPDText(\
					': (Spriteptr = '))
			_view_writer.write_hex(spriteptr)
		EUDEndIf()

		# print player, unit
		pid = f_bread_epd(epd + (0x4C // 4), 0)
		unitid = f_wread_epd(epd + (0x64 // 4), 0)


		_view_writer.write_strepd(makeEPDText(') player = P'))
		_view_writer.write_decimal(pid + 1)

		_view_writer.write_strepd(makeEPDText(' unit = '))
		unitname_epd = EUDVariable()
		if EUDIf()(SearchTableInv(unitid, EPD(tb_unitMap), \
				EPD(unitname_epd.getValueAddr())) == 1):
			_view_writer.write_strepd(unitname_epd)
		if EUDElseIf()(SearchTableInv(unitid, EPD(tb_unit), \
				EPD(unitname_epd.getValueAddr())) == 1):
			_view_writer.write_strepd(unitname_epd)
		if EUDElse()():
			_view_writer.write_decimal(unitid)
		EUDEndIf()
		_view_writer.write(ord('\n'))

		DoActions([
			off.AddNumber(1),
			ptr.AddNumber(336),
			epd.AddNumber(336//4),
		])
	EUDEndInfLoop()

	# make empty lines
	if EUDInfLoop()():
		EUDBreakIf(off >= pageend)
		_view_writer.write(ord('\n'))
		DoActions(off.AddNumber(1))
	EUDEndInfLoop()

	_view_writer.write(0)
	EUDReturn(1)

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_get_bufepd(members):
	EUDReturn(members.screen_data_epd)

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_destructor(members):
	dbpool.free_epd(members.screen_data_epd)
	varpool.free(members)

UnitArrayView = EUDView(
	unitarrayview_init,
	unitarrayview_keydown_callback,
	unitarrayview_execute_chat,
	unitarrayview_loop,
	unitarrayview_get_bufepd,
	unitarrayview_destructor
)
