from eudplib import *
from .view import _view_writer, EUDView, varpool
from ..core.command import EUDCommandPtr
from ..core.table import ReferenceTable
from ..core.scrollview import ScrollView
from .static import (
	StaticViewMembers,
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_loop,
	staticview_display,
	staticview_destructor,
)

@EUDFunc
def tableDec_StringDecimal(name, val):
	_view_writer.write_f("%E: %D", name, val)

@EUDFunc
def tableDec_StringHex(name, val):
	_view_writer.write_f("%E: %H", name, val)

@EUDFunc
def tableDec_String(name, val):
	_view_writer.write_strepd(name)

@EUDFunc
def tableDec_Command(name, val):
	_view_writer.write_f("%E - %E",
		name,
		EUDCommandPtr.cast(val)._doc_epd
	)

# use StaticViewMembers
varn = len(StaticViewMembers._fields_)

@EUDFunc
def tableview_init(arr_epd):
	'''
	epd-pointer of EUDArray: title_epd, decoder, table_epd

	decoder is writing function with param (offset, key, value)

	table_epd is epd-pointer of	ReferenceTable
	table_sz(=N), key1, value1, key2, value2, ..., keyN, valueN
	'''
	members = StaticViewMembers.cast(varpool.alloc(varn))

	members.title_epd = f_dwread_epd(arr_epd)
	decoder = EUDFuncPtr(2, 0)(f_dwread_epd(arr_epd + 1))

	# read table
	table_epd = f_dwread_epd(arr_epd + 2)
	table_sz = f_dwread_epd(table_epd)
	scrollview = ScrollView(table_sz)

	def table_iter(cur, name_epd, value_epd):
		_view_writer.seekepd(scrollview.GetEPDLine(cur))
		decoder(f_dwread_epd(name_epd), f_dwread_epd(value_epd))
		_view_writer.write(0)

	ReferenceTable.Iter(table_epd, table_iter)
	members.scrollview = scrollview
	EUDReturn(members)

TableView = EUDView(
	tableview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_loop,
	staticview_display,
	staticview_destructor
)
