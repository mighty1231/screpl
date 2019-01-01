from eudplib import *
from .view import _view_writer, EUDView
from ..utils import makeEPDText, f_epd2ptr
from .table import (
	TableViewMembers,
	PAGE_NUMCONTENTS,
	tableview_init,
	tableview_keydown_callback,
	tableview_execute_chat,
	tableview_get_bufepd,
	tableview_destructor
)

# decoder in loop is unused
@EUDTypedFunc([TableViewMembers])
def variableview_loop(members):
	# refresh all time
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
		_view_writer.write_strepd(f_dwread_epd(name_epd))
		_view_writer.write_strepd(makeEPDText(' (addr = '))
		variable_epd = f_dwread_epd(value_epd)
		_view_writer.write_hex(f_epd2ptr(variable_epd))
		_view_writer.write_strepd(makeEPDText(' ): '))
		v = f_dwread_epd(variable_epd)
		_view_writer.write_hex(v)
		_view_writer.write_strepd(makeEPDText(' = '))
		_view_writer.write_decimal(v)
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

VariableView = EUDView(
	tableview_init,
	tableview_keydown_callback,
	tableview_execute_chat,
	variableview_loop,
	tableview_get_bufepd,
	tableview_destructor
)
