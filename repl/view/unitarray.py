from eudplib import *
from .view import _view_writer, EUDView, varpool
from .static import StaticView
from ..utils import EPDConstString, f_strcmp_ptrepd, f_print_utf8_epd
from ..core.encoder import ReadNumber
from ..core.scrollview import ScrollView

class UnitArrayViewMembers(EUDStruct):
	_fields_ = [
		# state variables
		'offset', # 0 ~ 1699 -> 0x59CCA8 + 336*i

		('scrollview', ScrollView)
	]

varn = len(UnitArrayViewMembers._fields_)

@EUDFunc
def unitarrayview_init(unused):
	members = UnitArrayViewMembers.cast(varpool.alloc(varn))
	members.offset = 0
	members.scrollview = ScrollView(8)
	EUDReturn(members)

@EUDTypedFunc([UnitArrayViewMembers, None])
def unitarrayview_keydown_callback(members, keycode):
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7
		if EUDIf()(members.offset >= 8):
			# find smaller offset
			orderid_epd = EPD(0x59CCA8 + 0x4D) + (336 // 4) * members.offset
			if EUDInfLoop()():
				members.offset -= 1
				DoActions(orderid_epd.SubtractNumber(336 // 4))
				EUDBreakIf(members.offset == 7)
				EUDBreakIf(MemoryXEPD(orderid_epd, AtLeast, 0x100, 0xFF00))
			EUDEndInfLoop()
			members.offset -= 7
		if EUDElseIf()(members.offset == 0):
			members.offset = 1692
		if EUDElse()():
			members.offset = 0
		EUDEndIf()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8
		if EUDIf()(members.offset <= 1692-8):
			# find bigger offset
			members.offset += 8
			orderid_epd = EPD(0x59CCA8 + 0x4D) + (336 // 4) * members.offset
			if EUDInfLoop()():
				EUDBreakIf(members.offset == 1692)
				members.offset += 1
				DoActions(orderid_epd.AddNumber(336 // 4))
				EUDBreakIf(MemoryXEPD(orderid_epd, AtLeast, 0x100, 0xFF00))
			EUDEndInfLoop()
		if EUDElseIf()(members.offset == 1692):
			members.offset = 0
		if EUDElse()():
			members.offset = 1692
		EUDEndIf()
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([UnitArrayViewMembers, None])
def unitarrayview_execute_chat(members, offset):
	# ? -> open view for help
	# ## -> set index to it
	new_idx = EUDVariable()
	if EUDIf()(ReadNumber(offset, 0, EPD(offset.getValueAddr()), \
			EPD(new_idx.getValueAddr())) == 1):
		if EUDIf()([new_idx <= 1692]):
			members.offset = new_idx
		if EUDElse()():
			members.offset = 1692
		EUDEndIf()
		EUDReturn(1)
	if EUDElseIf()(f_strcmp_ptrepd(offset, EPDConstString("?")) == 0):
		args = EUDArray([
			EPDConstString("UNITARRAY VIEW - Manual"),
			7,
			EPDConstString("Keycode"),
			EPDConstString("F7: Go to smaller offset"),
			EPDConstString("F8: Go to bigger offset"),
			EPDConstString(""),
			EPDConstString("Type"),
			EPDConstString("?: get help"),
			EPDConstString("##: go to 0x59CCA8 + 336 * ##"),
		])
		StaticView.OpenView(EPD(args))
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_loop(members):
	# title line
	off = members.offset
	sv = members.scrollview

	unit_ptr = 0x59CCA8 + 336 * off
	unit_epd = EPD(0x59CCA8) + (336 // 4) * off
	i = EUDVariable()
	i << 0
	if EUDWhile()(i < 8):
		_view_writer.seekepd(sv.GetEPDLine(i))

		# check Dead
		_view_writer.write_f("%C%H(i=%D): ", 0x16, unit_ptr, off + i)
		if EUDIf()(MemoryXEPD(unit_epd + (0x4D // 4), Exactly, 0, 0xFF00)):
			_view_writer.write_f("Dead%C", 0)
		if EUDElse()():
			from ..resources.decoder.common import writeUnit
			_view_writer.write_f("player = P%D unit = ",
				f_bread_epd(unit_epd + 0x4C // 4, 0) + 1)
			writeUnit(f_wread_epd(unit_epd + (0x64 // 4), 0))
			_view_writer.write(0)
		EUDEndIf()

		DoActions([
			unit_ptr.AddNumber(336),
			unit_epd.AddNumber(336 // 4),
			i.AddNumber(1),
		])
	EUDEndWhile()

	EUDReturn()

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_display(members):
	title = Db(218)
	_view_writer.seekepd(EPD(title))
	_view_writer.write_f('CUnit-array View, type "?" for help, i = %D (0 ~ 1699)%C',
		members.offset, 0)

	f_print_utf8_epd(EPD(title))
	members.scrollview.Display()

@EUDTypedFunc([UnitArrayViewMembers])
def unitarrayview_destructor(members):
	members.scrollview.Destruct()
	varpool.free(members)

UnitArrayView = EUDView(
	unitarrayview_init,
	unitarrayview_keydown_callback,
	unitarrayview_execute_chat,
	unitarrayview_loop,
	unitarrayview_display,
	unitarrayview_destructor
)
