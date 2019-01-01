from eudplib import *
from ..resources.pool import getVarPool, getDbPool
from .view import _view_writer, EUDView
from ..utils import makeEPDText
from ..core.command import EUDCommandPtr

LINESIZE = 216
PAGE_NUMCONTENTS = 8

@EUDFunc
def tableDec_StringDecimal(name, val):
    _view_writer.write_strepd(name)
    _view_writer.write_strepd(makeEPDText(': '))
    _view_writer.write_decimal(val)

@EUDFunc
def tableDec_StringHex(name, val):
    _view_writer.write_strepd(name)
    _view_writer.write_strepd(makeEPDText(': '))
    _view_writer.write_hex(val)

@EUDFunc
def tableDec_String(name, val):
    _view_writer.write_strepd(name)

@EUDFunc
def tableDec_Command(name, val):
    _view_writer.write_strepd(name)
    _view_writer.write_strepd(makeEPDText(" - "))
    _view_writer.write_strepd(
        EUDCommandPtr.cast(val)._doc_epd)


class TableViewMembers(EUDStruct):
	_fields_ = [
		# epd-pointer to title
		'title_epd',

		# total lines
		'table_sz',
		'table_epd',
		('decoder', EUDFuncPtr(2, 0)),
		'num_pages',

		# buffer for current screen
		'screen_data_epd',
		'update',

		# state variables
		'offset',
		'cur_page',
	]

varn = len(TableViewMembers._fields_)

@EUDFunc
def tableview_init(arr_epd):
	'''
	epd-pointer of EUDArray: title_epd, decoder, table_epd

	decoder is writing function with param (offset, key, value)

	table_epd is epd-pointer of	ReferenceTable
	table_sz(=N), key1, value1, key2, value2, ..., keyN, valueN
	'''
	members = TableViewMembers.cast(getVarPool().alloc(varn))

	members.title_epd = f_dwread_epd(arr_epd)
	members.decoder = f_dwread_epd(arr_epd + 1)

	# read table
	table_epd = f_dwread_epd(arr_epd + 2)
	table_sz = f_dwread_epd(table_epd)
	members.num_pages = f_div(table_sz + PAGE_NUMCONTENTS - 1, \
		PAGE_NUMCONTENTS)[0]
	members.table_epd = table_epd
	members.table_sz = table_sz

	# screen buffer
	members.screen_data_epd = getDbPool().alloc_epd(\
		LINESIZE * (PAGE_NUMCONTENTS + 1))
	members.update = 1

	# variables for current state
	members.offset = 0
	members.cur_page = 0

	EUDReturn(members)

@EUDTypedFunc([TableViewMembers, None])
def tableview_keydown_callback(members, keycode):
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

@EUDTypedFunc([TableViewMembers, None])
def tableview_execute_chat(members, offset):
	EUDReturn(0)

@EUDTypedFunc([TableViewMembers])
def tableview_loop(members):
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
		if EUDIf()(pageend >= members.table_sz):
			until << members.table_sz
		if EUDElse()():
			until << pageend
		EUDEndIf()

		name_epd = members.table_epd + 2 * members.offset + 1
		value_epd = name_epd + 1

		if EUDInfLoop()():
			EUDBreakIf(cur >= until)
			members.decoder(f_dwread_epd(name_epd), f_dwread_epd(value_epd))
			_view_writer.write(ord('\n'))

			DoActions([
				cur.AddNumber(1),
				name_epd.AddNumber(2),
				value_epd.AddNumber(2),
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

@EUDTypedFunc([TableViewMembers])
def tableview_get_bufepd(members):
	EUDReturn(members.screen_data_epd)

@EUDTypedFunc([TableViewMembers])
def tableview_destructor(members):
	getDbPool().free_epd(members.screen_data_epd)
	getVarPool().free(members)

TableView = EUDView(
	tableview_init,
	tableview_keydown_callback,
	tableview_execute_chat,
	tableview_loop,
	tableview_get_bufepd,
	tableview_destructor
)
