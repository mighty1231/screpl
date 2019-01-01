from eudplib import *
from ..utils.utils import f_strlen
from ..core.command import runCommand
from .board import Board
from ..resources.table.tables import repl_commands
from ..resources.command.basics import register_basiccmds
from ..resources.command.conditions import register_all_conditioncmds
from ..resources.command.actions import register_all_actioncmds
from ..resources.command.utils import register_utilcmds
from ..view.view import GetCurrentView, TerminateCurrentView, EUDView
from ..utils import EUDByteRW, makeEPDText

_repl = None
PAGE_NUMLINES = 8
LINESIZE = 216
REPLSIZE = 300

class REPL:
	def __init__(self, superuser = P1):
		global _repl 
		assert _repl == None, "REPL instance should be unique"
		_repl = self

		self.display = EUDVariable(1)

		# superuser's name
		# assert isinstance(superuser, str), 'must be string'
		# self.prefix = makeEPDText(EPD(superuser + ':'))
		# self.prefixlen = len(superuser + ':')
		self.playerId = EncodePlayer(superuser)
		assert 0 <= self.playerId < 8, "Superuser should be one of P1 ~ P8"
		self.prefix = Db(26)
		self.prefixlen = EUDVariable()
		self.board = Board.GetInstance()

		# Itself is a view
		self.writer = EUDByteRW()
		self.page = DBString(5000)
		inittitle = u2b('SC-REPL, type help()')
		self.title = Db(inittitle + bytes(100-len(inittitle)))
		self.update = EUDVariable(1)
		self.repl_input = Db(LINESIZE*REPLSIZE)
		self.repl_output = Db(LINESIZE*REPLSIZE)
		self.repl_inputEPDPtr = EUDVariable(EPD(self.repl_input))
		self.repl_outputEPDPtr = EUDVariable(EPD(self.repl_output))
		self.repl_index = EUDVariable() # increases for every I/O from 0

		# Variables for current REPL page
		self.repl_top_index = EUDVariable() # index of topmost at a page
		self.repl_cur_page = EUDVariable()

		# repl visual
		self.repl_outputcolor = 0x16

		# Views
		self.mode = EUDVariable(0) # 0 if there is no view, else 1
		self.view = EUDVariable(0)
		self.viewmem = EUDVariable(0)

		# these registering functions are python-functions
		register_basiccmds()
		register_utilcmds()
		register_all_conditioncmds()
		register_all_actioncmds()

	@EUDMethod
	def update_view(self):
		view, viewmem = GetCurrentView()
		if EUDIf()([self.mode == 1, viewmem == 0]):
			self.mode << 0
			self.update << 1
		if EUDElseIf()([self.mode == 0, viewmem >= 1]):
			self.mode << 1
		EUDEndIf()
		SetVariables([self.view, self.viewmem],\
			[view, viewmem])

	@EUDMethod
	def super_keydown_callback(self, keycode):
		EUDSwitch(keycode)
		if EUDSwitchCase()(0x78): # Display
			DoActions(SetMemoryX(self.display.getValueAddr(), Add, 1, 1))
			EUDBreak()
		if EUDSwitchCase()(0x1B): # ESC
			if EUDIf()(self.mode == 1):
				TerminateCurrentView()
				self.update_view()
			EUDEndIf()
			EUDBreak()
		EUDEndSwitch()

	@EUDMethod
	def keydown_callback(self, keycode):
		EUDSwitch(keycode)
		if EUDSwitchCase()(0x76): # prev page
			if EUDIfNot()(self.repl_top_index == 0):
				DoActions([
					self.repl_top_index.SubtractNumber( \
							PAGE_NUMLINES//2),
					self.repl_cur_page.SubtractNumber(1),
					self.update.SetNumber(1)
				])
			EUDEndIf()
			EUDBreak()
		if EUDSwitchCase()(0x77): # next page
			if EUDIf()((self.repl_top_index+(PAGE_NUMLINES//2+1)). \
						AtMost(self.repl_index)):
				DoActions([
					self.repl_top_index.AddNumber( \
							PAGE_NUMLINES//2),
					self.repl_cur_page.AddNumber(1),
					self.update.SetNumber(1)
				])
			EUDEndIf()
			EUDBreak()
		EUDEndSwitch()

	@EUDMethod
	def update_keystate(self):
		prev_keystate = Db(0x100)

		r1 = EUDByteRW()
		r2 = EUDByteRW()

		r1.seekepd(EPD(prev_keystate))
		r2.seekepd(EPD(0x596A18))
		keycode = EUDVariable()
		keycode << 0
		if EUDWhile()(keycode < 0x100):
			c1 = r1.read()
			c2 = r2.read()
			if EUDIf()([c2 == 1, c1 == 0]):
				self.super_keydown_callback(keycode)
				if EUDIf()(self.viewmem == 0):
					self.keydown_callback(keycode)
				if EUDElse()():
					EUDView.cast(self.view).keydown_callback(self.viewmem, keycode)
				EUDEndIf()
			EUDEndIf()
			DoActions(keycode.AddNumber(1))
		EUDEndWhile()
		f_repmovsd_epd(EPD(prev_keystate), EPD(0x596A18), 0x100//4)

	@EUDMethod
	def _execute_command(self, offset):
		# If it needs new page, then update current page
		# check repl_index % (8 // 2) == 0
		# repl_index at page 0: 0 1 2 3
		# repl_index at page 1: 4 5 6 7
		# repl_index at page 2: 8 9 10 11
		self.writer.seekepd(self.repl_inputEPDPtr)
		self.writer.write_str(offset)
		self.writer.write(0)
		runCommand(offset, EPD(repl_commands), self.repl_outputEPDPtr)
		quot, mod = f_div(self.repl_index, PAGE_NUMLINES // 2)
		self.repl_top_index << self.repl_index - mod
		self.repl_cur_page << quot
		DoActions([
			self.repl_inputEPDPtr.AddNumber(LINESIZE // 4),
			self.repl_outputEPDPtr.AddNumber(LINESIZE // 4),
			self.repl_index.AddNumber(1),
			self.update.SetNumber(1)
		])

	@EUDMethod
	def update_repl(self):
		if EUDIf()(self.update == 0):
			EUDReturn()
		EUDEndIf()

		# update
		self.writer.seekepd(EPD(self.page.GetStringMemoryAddr()))

		# Write title and page
		self.writer.write_strepd(EPD(self.title))
		self.writer.write_strepd(makeEPDText(' ( '))

		# REPL mode
		if EUDIf()(self.repl_index == 0):
			self.writer.write_decimal(0)
		if EUDElse()():
			self.writer.write_decimal(self.repl_cur_page + 1)
		EUDEndIf()
		self.writer.write_strepd(makeEPDText(' / '))
		self.writer.write_decimal(f_div(\
			self.repl_index + (PAGE_NUMLINES//2-1), 
			PAGE_NUMLINES//2)[0])
		self.writer.write_strepd(makeEPDText(' )\n'))

		# Write contents
		cur, inputepd, outputepd, until, pageend = EUDCreateVariables(5)
		cur << self.repl_top_index

		pageend << self.repl_top_index + PAGE_NUMLINES//2
		if EUDIf()(pageend >= self.repl_index):
			until << self.repl_index
		if EUDElse()():
			until << pageend
		EUDEndIf()

		off = (LINESIZE // 4) * cur
		inputepd << EPD(self.repl_input) + off
		outputepd << EPD(self.repl_output) + off
		if EUDInfLoop()():
			EUDBreakIf(cur >= until)

			self.writer.write_strepd(makeEPDText('\x1C>>> \x1D'))
			self.writer.write_strepd(inputepd)
			self.writer.write_strepd(makeEPDText('\n'))

			self.writer.write(self.repl_outputcolor)
			self.writer.write_strepd(outputepd)
			self.writer.write_strepd(makeEPDText('\n'))

			DoActions([
				cur.AddNumber(1),
				inputepd.AddNumber(LINESIZE // 4),
				outputepd.AddNumber(LINESIZE // 4),
			])
		EUDEndInfLoop()

		# make empty lines
		if EUDInfLoop()():
			EUDBreakIf(cur >= pageend)
			self.writer.write(ord('\n'))
			self.writer.write(ord('\n'))
			DoActions(cur.AddNumber(1))
		EUDEndInfLoop()
		self.writer.write(0)

	@EUDMethod
	def execute(self):
		'''
		Main part of REPL
		'''
		# update view
		# view may be constructed before
		self.update_view()

		# key callbacks
		# view may be terminated on here
		self.update_keystate()

		# Check whether user typed nothing
		self.prev_txtPtr = EUDVariable(initval=10)
		do_display = Forward()
		if EUDIf()(Memory(0x640B58, Exactly, self.prev_txtPtr)):
			EUDJump(do_display)
		EUDEndIf()

		# copy P1's name
		f_strcpy(self.prefix, 0x57EEEB + 36*self.playerId)
		self.prefixlen << f_strlen(0x57EEEB)

		cur_txtPtr = f_dwread_epd(EPD(0x640B58))
		i = EUDVariable()
		i << self.prev_txtPtr
		chat_off = 0x640B60 + 218 * i

		# process all new chats
		if EUDInfLoop()():
			EUDBreakIf(i == cur_txtPtr)
			if EUDIf()(f_memcmp(chat_off, self.prefix, self.prefixlen) == 0):
				new_chat_off = chat_off + (self.prefixlen + 2)
				if EUDIf()(self.viewmem == 0):
					self._execute_command(new_chat_off) # 2 from (colorcode, spacebar)
				if EUDElseIf()(EUDView.cast(self.view).execute_chat(self.viewmem, new_chat_off) == 0):
					self._execute_command(new_chat_off)
				EUDEndIf()
			EUDEndIf()
			if EUDIf()(i == 10):
				i << 0
				chat_off << 0x640B60
			if EUDElse()():
				i += 1
				chat_off += 218
			EUDEndIf()
		EUDEndInfLoop()
		self.prev_txtPtr << cur_txtPtr

		# loop
		do_display << NextTrigger()
		if EUDIf()(self.mode == 0):
			# REPL
			self.update_repl()
		if EUDElse()():
			# VIEW
			EUDView.cast(self.view).loop(self.viewmem)
			self.writer.seekepd(EPD(self.page.GetStringMemoryAddr()))
			self.writer.write_strepd( \
				EUDView.cast(self.view).get_bufepd(self.viewmem))
			self.writer.write(0)
		EUDEndIf()

		# display
		if EUDIf()(self.display == 1):
			# Print top of the screen, you can chat at the same time
			txtPtr = f_dwread_epd(EPD(0x640B58))

			f_setcurpl(EncodePlayer(self.playerId))
			self.page.Display()

			SeqCompute([(EPD(0x640B58), SetTo, txtPtr)])
		EUDEndIf()
