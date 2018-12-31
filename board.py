from eudplib import *
from utils import *

PAGE_NUMLINES = 8
BUFSIZE = 500
REPLSIZE = 300
LINESIZE = 216 # 218 in In-game

class Board:
	'''
	Announcement Board, top of chat. Note that Starcraft has total 11 lines on chatting
	Forms:
	line 0: [Title]
	line 1: content 1
	  ...
	line N: content N

	total PAGE_NUMLINES + 1 lines

	REPL page for default. pop-up for see some table contents
	'''
	instance = None

	# contents for line i is stored in db[i*LINESIZE:(i+1)*LINESIZE]
	assert PAGE_NUMLINES % 2 == 0, "Check convenience for REPL"
	assert LINESIZE % 4 == 0, "Check convenience"

	@staticmethod
	def GetInstance():
		if Board.instance == None:
			Board.instance = Board()
		return Board.instance

	def __init__(self):
		assert Board.instance == None

		self.writer = EUDByteRW()

		# Print a single page
		self.page = DBString(1024)
		inittitle = u2b('SC-REPL, type help()')
		self.title = Db(inittitle + bytes(100-len(inittitle)))

		# 1 if it needs to update page before display
		self.update = EUDVariable(1)

		# mode 0: REPL mode
		# mode 1: Static page mode
		self.mode = EUDVariable(0)

		# Store for REPL (main)
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

		# Buffer for static pages
		self.static_data = Db(LINESIZE*BUFSIZE)
		self.static_ln = EUDVariable()

		# offset ~ offset+PAGE_NUMLINES-1
		self.static_offset = EUDVariable()
		self.static_cur_page = EUDVariable()
		self.static_num_pages = EUDVariable()

	@EUDMethod
	def REPLReset(self):
		self.repl_inputEPDPtr << EPD(self.repl_input)
		self.repl_outputEPDPtr << EPD(self.repl_output)
		self.repl_index << 0
		self.repl_cur_page << 0

		if EUDIf()(self.mode == 0):
			self.update << 1
		EUDEndIf()

	@EUDMethod
	def REPLWriteInput(self, _input):
		self.writer.seekepd(self.repl_inputEPDPtr)
		self.writer.write_str(_input)
		self.writer.write(0)

	@EUDMethod
	def REPLWriteOutput(self, _output):
		self.writer.seekepd(self.repl_outputEPDPtr)
		self.writer.write_str(_output)
		self.writer.write(0)

	@EUDMethod
	def REPLCompleteEval(self):
		# If it needs new page, then update current page
		# check repl_index % (8 // 2) == 0
		# repl_index at page 0: 0 1 2 3
		# repl_index at page 1: 4 5 6 7
		# repl_index at page 2: 8 9 10 11
		quot, mod = f_div(self.repl_index, PAGE_NUMLINES // 2)
		self.repl_top_index << self.repl_index - mod
		self.repl_cur_page << quot

		DoActions([
			self.repl_inputEPDPtr.AddNumber(LINESIZE // 4),
			self.repl_outputEPDPtr.AddNumber(LINESIZE // 4),
			self.repl_index.AddNumber(1)
		])

		if EUDIf()(self.mode == 0):
			self.update << 1
		EUDEndIf()

	@EUDMethod
	def SetMode(self, mode):
		if EUDIfNot()(Memory(self.mode.getValueAddr(),Exactly, mode)):
			self.mode << mode
			self.update << 1

			if EUDIf()(self.mode == 0):
				self.SetTitle(makeText('SC-REPL'))
			EUDEndIf()
		EUDEndIf()

	@EUDTypedMethod([None, EUDFuncPtr(3, 0)])
	def SetContentWithTable_epd(self, table_epd, item_decoder):
		size = f_dwread_epd(table_epd)
		self.static_ln << size
		self.static_offset << 0
		self.static_cur_page << 0
		self.static_num_pages << f_div(size+PAGE_NUMLINES-1, PAGE_NUMLINES)[0]

		name_epd, val_epd, dest_ptr = EUDCreateVariables(3)
		DoActions([
			name_epd.SetNumber(table_epd),
			name_epd.AddNumber(1),
			val_epd.SetNumber(table_epd),
			val_epd.AddNumber(2),
			dest_ptr.SetNumber(self.static_data)
		])
		if EUDInfLoop()():
			EUDBreakIf(size == 0)
			item_decoder(dest_ptr, f_dwread_epd(name_epd), f_dwread_epd(val_epd))
			DoActions([
				size.SubtractNumber(1),
				name_epd.AddNumber(2),
				val_epd.AddNumber(2),
				dest_ptr.AddNumber(LINESIZE),
			])
		EUDEndInfLoop()

		if EUDIf()(self.mode == 1):
			self.update << 1
		EUDEndIf()

	@EUDTypedMethod([EUDArray, EUDVariable])
	def SetStaticContent(self, epdarr, cnt):
		'''
		epdarr[i] = EPD(Db(b'content_i_\0'))
		'''
		index, dest_epd = EUDCreateVariables(2)
		# DoActions([
		# 		index.SetNumber(0),
		# 		dest_epd.SetNumber(EPD(self.static_data))
		# 	])
		index << 0
		dest_epd << EPD(self.static_data)
		# LINESIZE BUFSIZE
		if EUDInfLoop()():
			EUDBreakIf(index >= cnt)
			self.writer.seekepd(dest_epd)
			self.writer.write_strepd(epdarr[index])
			self.writer.write(0)

			DoActions([
				index.AddNumber(1),
				dest_epd.AddNumber(LINESIZE // 4)
			])
		EUDEndInfLoop()
		self.static_ln << cnt
		self.static_offset << 0
		self.static_cur_page << 0
		self.static_num_pages << f_div(cnt+PAGE_NUMLINES-1, PAGE_NUMLINES)[0]

		if EUDIf()(self.mode == 1):
			self.update << 1
		EUDEndIf()

	@EUDMethod
	def UpdatePage(self):
		if EUDIf()(self.update == 0):
			EUDReturn()
		EUDEndIf()
		self.writer.seekepd(EPD(self.page.GetStringMemoryAddr()))

		# Write title and page
		self.writer.write_str(self.title)
		self.writer.write_str(makeText(' ( '))

		if EUDIf()(self.mode == 0):
			# REPL mode
			if EUDIf()(self.repl_index == 0):
				self.writer.write_decimal(0)
			if EUDElse()():
				self.writer.write_decimal(self.repl_cur_page + 1)
			EUDEndIf()
			self.writer.write_str(makeText(' / '))
			self.writer.write_decimal(f_div(\
				self.repl_index + (PAGE_NUMLINES//2-1), 
				PAGE_NUMLINES//2)[0])
			self.writer.write_str(makeText(' )\n'))

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

				self.writer.write_str(makeText('\x1C>>> \x1D'))
				self.writer.write_strepd(inputepd)
				self.writer.write_str(makeText('\n'))

				self.writer.write(self.repl_outputcolor)
				self.writer.write_strepd(outputepd)
				self.writer.write_str(makeText('\n'))

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
		if EUDElse()():
			# static mode
			if EUDIf()(self.static_num_pages == 0):
				self.writer.write_decimal(0)
			if EUDElse()():
				self.writer.write_decimal(self.static_cur_page + 1)
			EUDEndIf()
			self.writer.write_str(makeText(' / '))
			self.writer.write_decimal(self.static_num_pages)
			self.writer.write_str(makeText(' )\n'))

			# Write contents
			cur, pageend, until = EUDCreateVariables(3)
			cur << self.static_offset
			pageend << self.static_offset + PAGE_NUMLINES 
			if EUDIf()(pageend >= self.static_ln):
				until << self.static_ln
			if EUDElse()():
				until << pageend
			EUDEndIf()

			bufepd = EPD(self.static_data) + (LINESIZE // 4) * cur
			if EUDInfLoop()():
				EUDBreakIf(cur >= until)
				self.writer.write_strepd(bufepd)
				self.writer.write(ord('\n'))

				DoActions([
					cur.AddNumber(1),
					bufepd.AddNumber(LINESIZE // 4)
				])
			EUDEndInfLoop()

			# make empty lines
			if EUDInfLoop()():
				EUDBreakIf(cur >= pageend)
				self.writer.write(ord('\n'))
				DoActions(cur.AddNumber(1))
			EUDEndInfLoop()
		EUDEndIf()
		self.writer.write(0)
		self.update << 0

	@EUDMethod
	def SetPrevPage(self):
		if EUDIf()(self.mode == 0):
			if EUDIfNot()(self.repl_top_index == 0):
				DoActions([
					self.repl_top_index.SubtractNumber( \
							PAGE_NUMLINES//2),
					self.repl_cur_page.SubtractNumber(1)
				])
				self.update << 1
			EUDEndIf()
		if EUDElse()():
			if EUDIfNot()(self.static_cur_page == 0):
				self.static_offset -= PAGE_NUMLINES
				self.static_cur_page -= 1
				self.update << 1
			EUDEndIf()
		EUDEndIf()

	@EUDMethod
	def SetNextPage(self):
		if EUDIf()(self.mode == 0):
			if EUDIf()((self.repl_top_index+(PAGE_NUMLINES//2+1)). \
						AtMost(self.repl_index)):
				DoActions([
					self.repl_top_index.AddNumber( \
							PAGE_NUMLINES//2),
					self.repl_cur_page.AddNumber(1)
				])
				self.update << 1
			EUDEndIf()
		if EUDElse()():
			if EUDIf()((self.static_cur_page+2).AtMost(self.static_num_pages)):
				self.static_offset += PAGE_NUMLINES
				self.static_cur_page += 1
				self.update << 1
			EUDEndIf()
		EUDEndIf()

	@EUDMethod
	def SetTitle(self, ptr):
		self.writer.seekepd(EPD(self.title))
		self.writer.write_str(ptr)
		self.writer.write(0)
		self.update << 1

	def Display(self, pid):
		if EUDIf()(self.update == 1):
			self.UpdatePage()
		EUDEndIf()

		# Print top of the screen, you can chat at the same time
		txtPtr = f_dwread_epd(EPD(0x640B58))

		f_setcurpl(EncodePlayer(pid))
		self.page.Display()

		SeqCompute([(EPD(0x640B58), SetTo, txtPtr)])

	@EUDMethod
	def ClearBoard(self):
		self.board_linecnt << 0

	# @EUDMethod
	# def AddLine(self, strptr):
	# 	self.lines[self.linecnt] = strptr
	# 	self.linecnt += 1
	# 	self.num_pages += f_div(cnt+PAGE_NUMLINES-1, PAGE_NUMLINES)[0]
