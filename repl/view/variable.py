from eudplib import *
from .view import _view_writer, EUDView
from ..core.scrollview import ScrollView
from ..utils import f_epd2ptr
from .static import (
	staticview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_display,
	staticview_destructor
)

class VariableViewMembers(EUDStruct):
	_fields_ = [
		# Two members are on top to override StaticViewMembers
		'title_epd',
		('scrollview', ScrollView),

		'table_epd', # EPD value for ReferenceTable of EUDVariable
	]

varn = len(VariableViewMembers._fields_)


@EUDFunc
def variableview_init(arr_epd):
	'''
	epd-pointer of EUDArray: title_epd, table_epd

	decoder is writing function with param (offset, key, value)

	table_epd is epd-pointer of	ReferenceTable
	table_sz(=N), key1, value1, key2, value2, ..., keyN, valueN
	'''
	members = VariableViewMembers.cast(varpool.alloc(varn))
	members.title_epd = f_dwread_epd(arr_epd)

	# read table
	table_epd = f_dwread_epd(arr_epd + 1)
	table_sz = f_dwread_epd(table_epd)
	scrollview = ScrollView(table_sz)

	members.table_epd = table_epd

	EUDReturn(members)

@EUDTypedFunc([VariableViewMembers])
def variableview_loop(members):
	if EUDIfNot()(members.scrollview.disp_lcnt == 0):
		for i, line_epd in members.scrollview.PageLoop():
			_view_writer.seekepd(line_epd)
			key_epd = members.table_epd + 2*i + 1
			value_epd = key_epd + 1
			variable_epd = f_dwread_epd(value_epd)
			variable_value = f_dwread_epd(variable_epd)
			_view_writer.write_f("%E (addr = %H): %H = %D%C",
				f_dwread_epd(key_epd),
				f_epd2ptr(variable_epd),
				variable_value,
				variable_value,
				0
			)
	EUDEndIf()


VariableView = EUDView(
	staticview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	variableview_loop,
	staticview_display,
	staticview_destructor
)
