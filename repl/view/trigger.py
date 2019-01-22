from eudplib import *
from .static import StaticView
from ..utils import EPDConstString, f_strcmp_ptrepd, f_print_utf8_epd
from ..core.encoder import ReadNumber
from ..core.scrollview import ScrollView
from ..core.view import _view_writer, EUDView, varpool
from ..resources.decoder.trigcond import dec_Condition
from ..resources.decoder.trigact import dec_Action

'''
Trigger
      Condition conditions[16];
      Action    actions[64];
      DWORD     dwExecutionFlags;
      BYTE      bExecuteFor[PlayerGroups::Max];
      BYTE      bCurrentActionIndex;
'''
class PayloadSizeObj(EUDObject):
	def GetDataSize(self):
		return 4

	def CollectDependency(self, emitbuffer):
		pass

	def WritePayload(self, emitbuffer):
		from eudplib.core.allocator.payload import _payload_size
		print('payload size', _payload_size)
		emitbuffer.WriteDword(_payload_size)

str_sect, str_size = EUDCreateVariables(2)
psobj = PayloadSizeObj()

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

	# trigger flags
	# https://github.com/bwapi/bwapi/blob/master/bwapi/BWAPI/Source/BW/Triggers.h
	flags = f_dwread_epd(members.epd + (8 + 16*20 + 64*32) // 4)
	_view_writer.seekepd(sv.GetEPDLine(line))
	_view_writer.write_f("Flags [ ")
	if EUDIf()(flags.ExactlyX(0x01, 0x01)):
		_view_writer.write_f("ExecuteActions(actindex=%D) ",
			f_bread_epd(members.epd + (8 + 16*20 + 64*32 + 4 + 27) // 4, 3))
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x02, 0x02)):
		_view_writer.write_f("IgnoreDefeat ")
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x04, 0x04)):
		_view_writer.write_f("PreserveTrigger ")
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x08, 0x08)):
		_view_writer.write_f("IgnoreExecution ")
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x10, 0x10)):
		_view_writer.write_f("SkipUIActions ")
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x20, 0x20)):
		_view_writer.write_f("PausedGame ")
	EUDEndIf()
	if EUDIf()(flags.ExactlyX(0x40, 0x40)):
		_view_writer.write_f("DisableWaitSkip ")
	EUDEndIf()
	_view_writer.write(ord("]"))
	_view_writer.write(0)
	line += 1

	_view_writer.seekepd(sv.GetEPDLine(line))
	_view_writer.write_f("Conditions%C", 0)
	line += 1

	# conditions
	cur_epd = members.epd + 8 // 4
	if EUDLoopN()(16):
		# check condtype = 0
		EUDBreakIf(MemoryXEPD(cur_epd + 3, Exactly, 0, 0xFF000000))
		_view_writer.seekepd(sv.GetEPDLine(line))
		_view_writer.write_strepd(EPDConstString(' - '))
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
		_view_writer.write_strepd(EPDConstString(' - '))
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
	members.scrollview = ScrollView(1+1+16+1+64+1)
	_update_view(members)
	EUDReturn(members)

@EUDTypedFunc([TriggerViewMembers, None])
def triggerview_keydown_callback(members, keycode):
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
	if EUDSwitchCase()(78): # N - Next trigger
		ptr, epd = f_dwepdread_epd(members.epd + 1)
		if EUDIf()([ptr <= 0x7FFFFFFF]):
			members.ptr = ptr
			members.epd = epd
			_update_view(members)
		EUDEndIf()
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([TriggerViewMembers, None])
def triggerview_execute_chat(members, offset):
	# ? -> open view for help
	# ## -> set pointer address of trigger to ##
	new_ptr = EUDVariable()
	if EUDIf()(ReadNumber(offset, 0, EPD(offset.getValueAddr()), \
			EPD(new_ptr.getValueAddr())) == 1):
		# Basic check normal trigger pointer
		if EUDIf()([
				new_ptr.ExactlyX(0, 0b11),
				new_ptr <= 0x7FFFFFFF]):
			members.ptr = new_ptr
			members.epd = EPD(new_ptr)
			_update_view(members)
			EUDReturn(1)
		if EUDElse()():
			EUDReturn(0)
		EUDEndIf()
	if EUDElseIf()(f_strcmp_ptrepd(offset, EPDConstString("?")) == 0):
		args = EUDArray([
			EPDConstString("TRIGGER VIEW - Manual"),
			9,
			EPDConstString("Keycode"),
			EPDConstString("F7: Go to left page"),
			EPDConstString("F8: Go to right page"),
			EPDConstString("R: Refresh trigger"),
			EPDConstString("N: Goto next trigger"),
			EPDConstString(""),
			EPDConstString("Type"),
			EPDConstString("?: get help"),
			EPDConstString("##: set pointer address of trigger to ##"),
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
			'ptr = %H, next = %H, line = %D',
			ptr, f_dwread_epd(epd+1), sv.offset)

	if EUDExecuteOnce()():
		str_sect = f_dwread_epd(EPD(0x5993D4))
		str_size = f_dwread_epd(EPD(psobj))
	EUDEndExecuteOnce()
	if EUDIf()([str_sect <= ptr, ptr <= str_sect + str_size]):
		_view_writer.write_f(', type = STR%C', 0)
	if EUDElse()():
		_view_writer.write_f(', type = TRIG%C', 0)
	EUDEndIf()

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
