from eudplib import *
from .static import (
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_display,
	staticview_destructor
)
from ..core.scrollview import ScrollView
from ..core.table import ReferenceTable
from ..core.view import _view_writer, EUDView, varpool
from ..utils import f_epd2ptr, EPDConstString

class VariableViewMembers(EUDStruct):
	_fields_ = [
		# Two members are on top to override StaticViewMembers
		'title_epd',
		('scrollview', ScrollView),

		'table_epd', # EPD value for ReferenceTable of EUDVariable
	]

varn = len(VariableViewMembers._fields_)


@EUDFunc
def variableview_init(table_epd):
	'''
	table_epd is epd-pointer of	ReferenceTable
	table_sz(=N), key1, value1, key2, value2, ..., keyN, valueN
	'''
	members = VariableViewMembers.cast(varpool.alloc(varn))
	members.title_epd = EPDConstString("Variables")

	# read table
	table_sz = ReferenceTable.GetSize(table_epd)
	scrollview = ScrollView(table_sz)

	members.table_epd = table_epd
	members.scrollview = scrollview

	EUDReturn(members)

@EUDTypedFunc([VariableViewMembers])
def variableview_loop(members):
	scrollview = members.scrollview
	def table_iter(cur, name_epd, value_epd):
		_view_writer.seekepd(scrollview.GetEPDLine(cur))
		varaddr_epd = f_dwread_epd(value_epd)
		var_value = f_dwread_epd(varaddr_epd)
		_view_writer.write_f("%E (addr = %H): %H = %D%C",
				f_dwread_epd(name_epd),
				f_epd2ptr(varaddr_epd),
				var_value,
				var_value,
				0
			)
	ReferenceTable.Iter(members.table_epd, table_iter)


VariableView = EUDView(
	variableview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	variableview_loop,
	staticview_display,
	staticview_destructor
)
