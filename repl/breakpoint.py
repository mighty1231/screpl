from eudplib import *
from eudplib.maprw.injector.mainloop import jumper
from .view import TriggerView
from .repl import repl_begin, repl_end
from .core.table import ReferenceTable
from .core.command import EUDCommand
from .resources.table.tables import RegisterCommand
from .utils import EPDConstString

bp_locked = EUDVariable(0)

# Instances used during break time
bp_cp = EUDVariable()
bp_trig_ptr = EUDVariable()


bp_table = ReferenceTable()

class BPItem(EUDStruct):
	_fields_ = [
		'name_epd',
		'turnout_trig_epd',
		'callback_ptr',
		'breaked_trig_ptr',
	]
repl_end_hook = None
repl_end_orig_nxt = EUDVariable(0)
jumper_orig_nxt = EUDVariable()

# Single turnout trigger
def RegisterBPHere(name, cond = None):
	global bp_table, repl_end_hook, repl_end_orig_nxt
	breaked_trig_ptr = Forward()
	empty_trig = RawTrigger()

	# make hook for repl_end
	if repl_end_hook is None:
		# automatically set EUDCommands for Breakpoint
		RegisterCommand('bpon', BPOn)
		RegisterCommand('bpoff', BPOff)
		RegisterCommand('bpcon', BPContinue)

		if PushTriggerScope():
			repl_end_hook = NextTrigger()
			if EUDIf()(bp_locked == 1):
				# Make infinite loop on repl
				DoActions(SetNextPtr(jumper, repl_begin))
				EUDJump(0x80000000)
			if EUDElseIf()([bp_locked == 0, bp_trig_ptr >= 1]):
				# continue
				DoActions(SetNextPtr(jumper, jumper_orig_nxt))
				tmp = EUDVariable()
				tmp << bp_trig_ptr
				bp_trig_ptr << 0

				# recover context
				f_setcurpl(bp_cp)

				# jump to breakpoint trigger
				EUDJump(tmp)
			if EUDElse()():
				# normal way
				EUDJump(repl_end_orig_nxt)
			EUDEndIf()
		PopTriggerScope()

	# construct callback
	if PushTriggerScope():
		callback_ptr = NextTrigger()
		DoActions(SetNextPtr(empty_trig, breaked_trig_ptr))

		# Conditional breakpoint
		if cond is not None:
			EUDIf()(cond)

		# recover original loop
		BPDeactivateHooks()

		# set repl only mode
		bp_locked << 1
		bp_cp << f_getcurpl()
		bp_trig_ptr << breaked_trig_ptr

		# Uses triggerview temporarily
		# @TODO make BPView
		TriggerView.OpenView(breaked_trig_ptr)

		# Make infinite loop on repl and pass it
		# Similar to EUDDoEvents, but starting trigger is different
		if EUDIf()(repl_end_orig_nxt == 0):
			repl_end_orig_nxt << f_dwread_epd(EPD(repl_end + 4))
		EUDEndIf()
		jumper_orig_nxt << f_dwread_epd(EPD(jumper + 4))
		DoActions([
			SetNextPtr(repl_end, repl_end_hook),
			SetNextPtr(jumper, repl_begin)
		])
		EUDJump(repl_begin)

		if cond != None:
			EUDEndIf()
	PopTriggerScope()
	breaked_trig_ptr << NextTrigger()

	# register
	struct = BPItem(_from = EUDVArray(4)([
			EPDConstString(name),
			EPD(empty_trig),
			callback_ptr,
			breaked_trig_ptr
	]))
	bp_table.AddPair(breaked_trig_ptr, struct)

@EUDFunc
def BPActivateHooks():
	global bp_table
	i = EUDVariable()
	i = f_dwread_epd(EPD(bp_table))
	item_epd = EUDVariable()
	item_epd << EPD(bp_table) + 2
	if EUDWhile()(i >= 1):
		item = BPItem.cast(f_dwread_epd(item_epd))

		# patch nextptr
		f_dwwrite_epd(item.turnout_trig_epd + 1, item.callback_ptr)

		item_epd += 2
		i -= 1
	EUDEndWhile()

@EUDFunc
def BPDeactivateHooks():
	global bp_table
	i = EUDVariable()
	i = f_dwread_epd(EPD(bp_table))
	item_epd = EUDVariable()
	item_epd << EPD(bp_table) + 2
	if EUDWhile()(i >= 1):
		item = BPItem.cast(f_dwread_epd(item_epd))

		# patch nextptr
		f_dwwrite_epd(item.turnout_trig_epd + 1, item.breaked_trig_ptr)

		item_epd += 2
		i -= 1
	EUDEndWhile()

@EUDCommand([])
def BPOn():
	BPActivateHooks()

@EUDCommand([])
def BPOff():
	global bp_locked
	BPDeactivateHooks()
	bp_locked << 0

# "Stepinto" is difficult, since we can't track
#   self_nextptr_modifying_trigger
@EUDCommand([])
def BPContinue():
	# run bp_trigger with single time and refresh bp_trig
	global bp_table, bp_cp, bp_trig_ptr

	if EUDIf()(bp_locked == 1):
		# set original loop mode
		BPActivateHooks()
		bp_locked << 0
	EUDEndIf()
