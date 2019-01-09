from eudplib import *
from .view import _view_writer, EUDView, dbpool, varpool
from .static import StaticView
from ..utils import makeEPDText, f_strcmp_ptrepd
from ..core.table import ReferenceTable, SearchTableInv
from ..core.encoder import ReadName, ReadNumber
from ..resources.table.tables import tb_Modifier, tb_Comparison

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
		_view_writer.write_strepd(makeEPDText('Action('))
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

		# for trigger lines
		# intermediate buffer between trigger and screen buffer
		'line_cnt',
		'line_epd',
		'refresh_lines',

		# buffer for current screen
		'screen_data_epd',
		'offset',
	]

varn = len(TriggerViewMembers._fields_)

@EUDFunc
def triggerview_init(ptr):
	members = TriggerViewMembers.cast(varpool.alloc(varn))
	members.ptr = ptr
	members.epd = EPD(ptr)

	members.line_epd = dbpool.alloc_epd( \
		LINESIZE * (1+16+1+64+1))

	members.screen_data_epd = dbpool.alloc_epd( \
		LINESIZE * (PAGE_NUMCONTENTS + 1))
	members.offset = 0
	members.refresh_lines = 1

	EUDReturn(members)

@EUDTypedFunc([TriggerViewMembers, None])
def triggerview_keydown_callback(members, keycode):
	# @TODO
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7 - Prev Page
		if EUDIf()(members.offset >= PAGE_NUMCONTENTS):
			members.offset -= PAGE_NUMCONTENTS
		if EUDElse()():
			members.offset = 0
		EUDEndIf()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8 - Next Page
		if EUDIf()(members.offset <= members.line_cnt - PAGE_NUMCONTENTS):
			members.offset += PAGE_NUMCONTENTS
		if EUDElse()():
			members.offset = members.line_cnt - 1
		EUDEndIf()
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
			members.offset = 0
			EUDReturn(1)
		if EUDElse()():
			EUDReturn(0)
		EUDEndIf()
	if EUDElseIf()(f_strcmp_ptrepd(offset, makeEPDText("?")) == 0):
		args = EUDArray([
			makeEPDText("TRIGGER VIEW"),
			9,
			makeEPDText("Keycode"),
			makeEPDText("F7: Go to left page"),
			makeEPDText("F8: Go to right page"),
			makeEPDText(""),
			makeEPDText("Type"),
			makeEPDText("?: get help"),
			makeEPDText("R: refresh trigger"),
			makeEPDText("next: set pointer to next trigger"),
			makeEPDText("(ptr): set pointer to trigger"),
		])
		StaticView.OpenView(EPD(args))
		EUDReturn(1)
	if EUDElseIf()(f_strcmp_ptrepd(offset, makeEPDText("R")) == 0):
		# @TODO refresh on demand
		members.refresh_lines = 1
		EUDReturn(1)
	if EUDElseIf()(f_strcmp_ptrepd(offset, makeEPDText("next")) == 0):
		members.offset = 0
		members.ptr, members.epd = f_dwepdread_epd(members.epd + 1)
		members.refresh_lines = 1
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDTypedFunc([TriggerViewMembers])
def triggerview_loop(members):
	# title line
	ptr = members.ptr
	epd = members.epd
	line_cnt = members.line_cnt
	line_epd = members.line_epd
	refresh_lines = members.refresh_lines
	screen_data_epd = members.screen_data_epd
	offset = members.offset

	# write on line buffer
	curline_epd, curtrig_epd = EUDCreateVariables(2)
	curline_epd << line_epd
	line_cnt << 0
	# write conditions
	_view_writer.seekepd(curline_epd)
	_view_writer.write_strepd(makeEPDText('CONDITIONS'))
	_view_writer.write(0)
	line_cnt += 1
	curline_epd += LINESIZE // 4
	curtrig_epd << epd + 8 // 4
	if EUDLoopN()(16):
		_view_writer.seekepd(curline_epd)
		EUDBreakIf(f_bread_epd(curtrig_epd + 3, 3) == 0)
		_view_writer.write_strepd(makeEPDText(' - '))
		DecodeCondition(curtrig_epd)

		line_cnt += 1
		curline_epd += LINESIZE // 4
		curtrig_epd += 20 // 4
	EUDEndLoopN()
	# write actions
	_view_writer.seekepd(curline_epd)
	_view_writer.write_strepd(makeEPDText('ACTIONS'))
	_view_writer.write(0)
	line_cnt += 1
	curline_epd += LINESIZE // 4
	curtrig_epd << epd + (8 + 16*20) // 4
	if EUDLoopN()(64):
		_view_writer.seekepd(curline_epd)
		EUDBreakIf(f_bread_epd(curtrig_epd + 6, 2) == 0)
		_view_writer.write_strepd(makeEPDText(' - '))
		DecodeAction(curtrig_epd)

		line_cnt += 1
		curline_epd += LINESIZE // 4
		curtrig_epd += 32 // 4
	EUDEndLoopN()
	# @TODO write flags
	# omit!

	# write on printing buffer
	_view_writer.seekepd(members.screen_data_epd)
	_view_writer.write_strepd(makeEPDText('Trigger View, type "?" for help, ptr = '))
	_view_writer.write_hex(ptr)
	_view_writer.write_strepd(makeEPDText(', next_ptr = '))
	_view_writer.write_hex(f_dwread_epd(epd+1))
	_view_writer.write_strepd(makeEPDText(', line = '))
	_view_writer.write_decimal(offset)
	_view_writer.write_strepd(makeEPDText('\n'))
	until = EUDVariable()
	pageend = offset + PAGE_NUMCONTENTS
	if EUDIf()(pageend >= line_cnt):
		until << line_cnt
	if EUDElse()():
		until << pageend
	EUDEndIf()

	line_epd += (offset * (LINESIZE // 4))
	if EUDInfLoop()():
		EUDBreakIf(offset >= until)
		_view_writer.write_strepd(line_epd)
		_view_writer.write(ord('\n'))

		DoActions([
			offset.AddNumber(1),
			line_epd.AddNumber(LINESIZE // 4),
		])
	EUDEndInfLoop()

	# make empty lines
	if EUDInfLoop()():
		EUDBreakIf(offset >= pageend)
		_view_writer.write(ord('\n'))
		DoActions(offset.AddNumber(1))
	EUDEndInfLoop()

	_view_writer.write(0)
	EUDReturn()

@EUDTypedFunc([TriggerViewMembers])
def triggerview_display(members):
	# EUDReturn(members.screen_data_epd)
	pass

@EUDTypedFunc([TriggerViewMembers])
def triggerview_destructor(members):
	dbpool.free_epd(members.screen_data_epd)
	dbpool.free_epd(members.line_epd)
	varpool.free(members)

TriggerView = EUDView(
	triggerview_init,
	triggerview_keydown_callback,
	triggerview_execute_chat,
	triggerview_loop,
	triggerview_display,
	triggerview_destructor
)
