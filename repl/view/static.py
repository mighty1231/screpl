from eudplib import *
from .view import _view_writer, EUDView, dbpool, varpool
from ..utils import makeEPDText, f_print_utf8_epd
from ..core.scrollview import ScrollView

class StaticViewMembers(EUDStruct):
	_fields_ = [
		'title_epd', # epd-pointer to title
		('scrollview', ScrollView)
	]

varn = len(StaticViewMembers._fields_)

@EUDFunc
def staticview_init(arr_epd):
	'''
	epd-pointer of EUDArray:
	title_epd, content_size(=N), content1, content2, ..., contentN
	'''
	members = StaticViewMembers.cast(varpool.alloc(varn))

	ln = f_dwread_epd(arr_epd + 1)
	members.title_epd = f_dwread_epd(arr_epd)
	members.scrollview = ScrollView(ln, arr_epd + 2)

	EUDReturn(members)

@EUDTypedFunc([StaticViewMembers, None])
def staticview_keydown_callback(members, keycode):
	EUDSwitch(keycode)
	if EUDSwitchCase()(0x76): # F7 - Prev Page
		members.scrollview.SetPrevPage()
		EUDBreak()
	if EUDSwitchCase()(0x77): # F8 - Next Page
		members.scrollview.SetNextPage()
		EUDBreak()
	EUDEndSwitch()

@EUDTypedFunc([StaticViewMembers, None])
def staticview_execute_chat(members, offset):
	EUDReturn(0)

@EUDTypedFunc([StaticViewMembers])
def staticview_loop(members):
	pass

@EUDTypedFunc([StaticViewMembers])
def staticview_display(members):
	top_epd = EPD(Db(216))

	_view_writer.seekepd(top_epd)
	sv = members.scrollview
	_view_writer.write_f("%E ( %D / %D )%C",
			members.title_epd, sv.offset, sv.disp_lcnt, 0)
	f_print_utf8_epd(top_epd)

	sv.Display()

@EUDTypedFunc([StaticViewMembers])
def staticview_destructor(members):
	members.scrollview.Destruct()
	varpool.free(members)

StaticView = EUDView(
	staticview_init,
	staticview_keydown_callback,
	staticview_execute_chat,
	staticview_loop,
	staticview_display,
	staticview_destructor
)
