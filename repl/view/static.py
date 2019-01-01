from eudplib import *
from ..resources.pool.varpool import getVarPool
from ..resources.pool.dbpool import getDbPool
from .view import _view_writer, EUDView
from ..utils import makeEPDText, f_dbepd_print
from ..resources.table.tables import RegisterView

LINESIZE = 216
PAGE_NUMCONTENTS = 8

class StaticViewMembers(EUDStruct):
	_fields_ = [
		# epd-pointer to title
		'title_epd',

		# total lines
		'ln',
		'lines_epd',
		'num_pages',

		# buffer for current screen
		'screen_data_epd',
		'update',

		# state variables
		'offset',
		'cur_page',
	]

varn = len(StaticViewMembers._fields_)

@EUDFunc
def staticview_init(arr_epd):
	'''
	EUDArray epd-pointer of 
	title_epd, content_size(=N), content1, content2, ..., contentN
	'''
	members = StaticViewMembers.cast(getVarPool().alloc(varn))

	ln = f_dwread_epd(arr_epd + 1)
	members.title_epd = f_dwread_epd(arr_epd)

	members.ln = ln
	members.lines_epd = arr_epd + 2
	members.num_pages = f_div(ln + PAGE_NUMCONTENTS - 1, \
		PAGE_NUMCONTENTS)[0]

	members.screen_data_epd = getDbPool().alloc_epd(\
		LINESIZE * PAGE_NUMCONTENTS)
	members.update = 1

	members.offset = 0
	members.cur_page = 0

	EUDReturn(members)

@EUDTypedFunc([StaticViewMembers, None])
def staticview_keydown_callback(members, keycode):
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7 - Prev Page
		if EUDIfNot()(members.cur_page == 0):
			members.offset -= PAGE_NUMCONTENTS
			members.cur_page -= 1
			members.update = 1
		EUDEndIf()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8 - Next Page
		if EUDIf()((members.cur_page+2).AtMost(members.num_pages)):
			members.offset += PAGE_NUMCONTENTS
			members.cur_page += 1
			members.update = 1
		EUDEndIf()
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([StaticViewMembers, None])
def staticview_execute_chat(members, offset):
	EUDReturn(0)

@EUDTypedFunc([StaticViewMembers])
def staticview_loop(members):
	# refresh
	if EUDIf()(members.update == 1):
		# title line
		_view_writer.seekepd(members.screen_data_epd)
		_view_writer.write_strepd(members.title_epd)
		_view_writer.write_strepd(makeEPDText(' ( '))
		if EUDIf()(members.num_pages == 0):
			_view_writer.write_decimal(0)
		if EUDElse()():
			_view_writer.write_decimal(members.cur_page + 1)
		EUDEndIf()
		_view_writer.write_strepd(makeEPDText(' / '))
		_view_writer.write_decimal(members.num_pages)
		_view_writer.write_strepd(makeEPDText(' )\n'))

		# write contents
		cur, pageend, until = EUDCreateVariables(3)
		cur << members.offset
		pageend << members.offset + PAGE_NUMCONTENTS 
		if EUDIf()(pageend >= members.ln):
			until << members.ln
		if EUDElse()():
			until << pageend
		EUDEndIf()

		bufepd = members.lines_epd + cur
		if EUDInfLoop()():
			EUDBreakIf(cur >= until)
			_view_writer.write_strepd(f_dwread_epd(bufepd))
			_view_writer.write(ord('\n'))

			DoActions([
				cur.AddNumber(1),
				bufepd.AddNumber(1)
			])
		EUDEndInfLoop()

		# make empty lines
		if EUDInfLoop()():
			EUDBreakIf(cur >= pageend)
			_view_writer.write(ord('\n'))
			DoActions(cur.AddNumber(1))
		EUDEndInfLoop()

		_view_writer.write(0)
		members.update = 0
		EUDReturn(1)
	EUDEndIf()
	EUDReturn(0)

@EUDTypedFunc([StaticViewMembers])
def staticview_get_bufepd(members):
	EUDReturn(members.screen_data_epd)

@EUDTypedFunc([StaticViewMembers])
def staticview_destructor(members):
	getDbPool().free_epd(members.screen_data_epd)
	getVarPool().free(members)

StaticView = EUDView(
	staticview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_loop,
	staticview_get_bufepd,
	staticview_destructor
)
