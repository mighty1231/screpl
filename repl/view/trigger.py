from eudplib import *
from .view import _view_writer, EUDView, dbpool, varpool
from .static import StaticView
from ..utils import makeEPDText, f_strcmp_ptrepd, f_print_utf8_epd
from ..core.table import ReferenceTable, SearchTableInv
from ..core.encoder import ReadName, ReadNumber
from ..core.scrollview import ScrollView
from ..resources.table.tables import tb_Modifier, tb_Comparison
from ..resources.decoder.trigcond import dec_Condition
from ..resources.decoder.trigact import dec_Action
from ..core.decoder import setOffset, setEPD

'''
Trigger
      Condition conditions[16];
      Action    actions[64];
      DWORD     dwExecutionFlags;
      BYTE      bExecuteFor[PlayerGroups::Max];
      BYTE      bCurrentActionIndex;
'''

LINESIZE = 216
PAGE_NUMCONTENTS = 8

@EUDFunc
def DecodeAction(act_epd):
	locid1             = f_dwread_epd(act_epd)
	strid              = f_dwread_epd(act_epd + 1)
	wavid              = f_dwread_epd(act_epd + 2)
	time               = f_dwread_epd(act_epd + 3)
	player1            = f_dwread_epd(act_epd + 4)
	player2            = f_dwread_epd(act_epd + 5)
	unitid             = f_wread_epd(act_epd + 6, 0)
	acttype            = f_bread_epd(act_epd + 6, 2)
	amount             = f_bread_epd(act_epd + 6, 3)
	flags_and_internal = f_dwread_epd(act_epd + 7)

	if EUDIf()(acttype == 45):
		_view_writer.write_strepd(makeEPDText('SetMemory('))

		# Offset
		_view_writer.write_hex(0x58A364 + 4*player1 + 48*unitid)
		_view_writer.write_strepd(makeEPDText(', '))

		# Modifier
		modname_epd = EUDVariable()
		SearchTableInv(amount, EPD(tb_Modifier), EPD(modname_epd.getValueAddr()))
		_view_writer.write_strepd(modname_epd)
		_view_writer.write_strepd(makeEPDText(', '))

		# Value
		_view_writer.write_decimal(player2)
		_view_writer.write_strepd(makeEPDText(')'))
	if EUDElse()():
		_view_writer.write_strepd(makeEPDText('Condition('))
		_view_writer.write_decimal(locid1)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(strid)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(wavid)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(time)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(player1)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(player2)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(unitid)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(acttype)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(amount)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(flags_and_internal)
		_view_writer.write_strepd(makeEPDText(')'))
	EUDEndIf()
	_view_writer.write(0)

@EUDFunc
def DecodeCondition(cond_epd):
	locid       = f_dwread_epd(cond_epd + 0)
	player      = f_dwread_epd(cond_epd + 1)
	amount      = f_dwread_epd(cond_epd + 2)
	unitid      = f_wread_epd(cond_epd + 3, 0)
	comparison  = f_bread_epd(cond_epd + 3, 2)
	condtype    = f_bread_epd(cond_epd + 3, 3)
	restype     = f_bread_epd(cond_epd + 4, 0)
	flags       = f_bread_epd(cond_epd + 4, 1)
	internal    = f_wread_epd(cond_epd + 4, 2)

	if EUDIf()(condtype == 15):
		_view_writer.write_strepd(makeEPDText('Memory('))

		# Offset
		_view_writer.write_hex(0x58A364 + 4*player + 48*unitid)
		_view_writer.write_strepd(makeEPDText(', '))

		# Comparison
		compname_epd = EUDVariable()
		SearchTableInv(comparison, EPD(tb_Comparison), EPD(compname_epd.getValueAddr()))
		_view_writer.write_strepd(compname_epd)
		_view_writer.write_strepd(makeEPDText(', '))

		# Value
		_view_writer.write_decimal(amount)
		_view_writer.write_strepd(makeEPDText(')'))
	if EUDElse()():
		_view_writer.write_strepd(makeEPDText('Action('))
		_view_writer.write_decimal(locid)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(player)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(amount)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(unitid)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(comparison)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(condtype)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(restype)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(flags)
		_view_writer.write_strepd(makeEPDText(', '))
		_view_writer.write_decimal(internal)
		_view_writer.write_strepd(makeEPDText(')'))
	EUDEndIf()
	_view_writer.write(0)


class TriggerViewMembers(EUDStruct):
	_fields_ = [
		# pointer to trigger
		'ptr',
		'epd',

		('scrollview', ScrollView),
	]

varn = len(TriggerViewMembers._fields_)

@EUDTypedFunc([TriggerViewMembers])
def _update_view(members):
	line = EUDVariable()
	line << 0

	sv = members.scrollview
	_view_writer.seekepd(sv.GetEPDLine(line))
	_view_writer.write_f("Conditions%C", 0)
	line += 1

	# conditions
	cur_epd = members.epd + 8 // 4
	if EUDLoopN()(16):
		# check condtype = 0
		EUDBreakIf(MemoryXEPD(cur_epd + 3, Exactly, 0, 0xFF000000))
		_view_writer.seekepd(sv.GetEPDLine(line))
		_view_writer.write_strepd(makeEPDText(' - '))
		setOffset(_view_writer.getoffset())
		dec_Condition(cur_epd)

		line += 1
		cur_epd += 20 // 4
	EUDEndLoopN()

	# actions
	_view_writer.seekepd(sv.GetEPDLine(line))
	_view_writer.write_f("Actions%C", 0)
	line += 1
	cur_epd << members.epd + (8 + 16*20) // 4
	if EUDLoopN()(64):
		# check acttype = 0
		EUDBreakIf(MemoryXEPD(cur_epd + 6, Exactly, 0, 0xFF0000))
		_view_writer.seekepd(sv.GetEPDLine(line))
		_view_writer.write_strepd(makeEPDText(' - '))
		setOffset(_view_writer.getoffset())
		dec_Action(cur_epd)

		line += 1
		cur_epd += 32 // 4
	EUDEndLoopN()

	_view_writer.seekepd(sv.GetEPDLine(line))
	_view_writer.write_f("END%C", 0)
	sv.SetDispLineCnt(line + 1)
	sv.offset = 0

@EUDFunc
def triggerview_init(ptr):
	members = TriggerViewMembers.cast(varpool.alloc(varn))
	members.ptr = ptr
	members.epd = EPD(ptr)
	members.scrollview = ScrollView(1+16+1+64+1)
	_update_view(members)
	EUDReturn(members)

@EUDTypedFunc([TriggerViewMembers, None])
def triggerview_keydown_callback(members, keycode):
	# @TODO
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7 - Prev Page
		members.scrollview.SetPrevPage()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8 - Next Page
		members.scrollview.SetNextPage()
		EUDBreak()
	if EUDSwitchCase()(82): # R - Refresh
		_update_view(members)
		EUDBreak()
	if EUDSwitchCase()(78): # R - Refresh
		members.ptr, members.epd = f_dwepdread_epd(members.epd + 1)
		_update_view(members)
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([TriggerViewMembers, None])
def triggerview_execute_chat(members, offset):
	# help -> open view for help
	# (number) -> set index to it (offset = 0 if index = 0 else 1700 - index)
	new_ptr = EUDVariable()
	if EUDIf()(ReadNumber(offset, 0, EPD(offset.getValueAddr()), \
			EPD(new_ptr.getValueAddr())) == 1):
		if EUDIf()(new_ptr.ExactlyX(0, 0b11)): # check normal trigger pointer
			members.ptr = new_ptr
			members.epd = EPD(new_ptr)
			_update_view(members)
			EUDReturn(1)
		if EUDElse()():
			EUDReturn(0)
		EUDEndIf()
	if EUDElseIf()(f_strcmp_ptrepd(offset, makeEPDText("?")) == 0):
		args = EUDArray([
			makeEPDText("TRIGGER VIEW - Manual"),
			9,
			makeEPDText("Keycode"),
			makeEPDText("F7: Go to left page"),
			makeEPDText("F8: Go to right page"),
			makeEPDText("R: Refresh trigger"),
			makeEPDText("N: Goto next trigger"),
			makeEPDText(""),
			makeEPDText("Type"),
			makeEPDText("?: get help"),
			makeEPDText("##: set pointer address of trigger to ##"),
		])
		StaticView.OpenView(EPD(args))
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDTypedFunc([TriggerViewMembers])
def triggerview_loop(members):
	pass

@EUDTypedFunc([TriggerViewMembers])
def triggerview_display(members):
	# EUDReturn(members.screen_data_epd)
	ptr = members.ptr
	epd = members.epd
	sv = members.scrollview

	title_epd = EPD(Db(218))
	_view_writer.seekepd(title_epd)
	_view_writer.write_f('Trigger View, type "?" for help. '\
			'ptr = %H, next = %H, line = %D%C',
			ptr, f_dwread_epd(epd+1), sv.offset, 0)

	f_print_utf8_epd(title_epd)

	members.scrollview.Display()

@EUDTypedFunc([TriggerViewMembers])
def triggerview_destructor(members):
	members.scrollview.Destruct()
	varpool.free(members)

TriggerView = EUDView(
	triggerview_init,
	triggerview_keydown_callback,
	triggerview_execute_chat,
	triggerview_loop,
	triggerview_display,
	triggerview_destructor
)
