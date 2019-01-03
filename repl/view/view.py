from eudplib import *
from ..utils import EUDByteRW, f_raiseError

'''
EUDView lifecycle
0. init
  if view is on foreground
     1. call keydown_callback if keydown is happened
        - if ESC button is pressed, the foreground window is
          destructed in the REPL context
     2. execute chats if chat exists
     3. loop
     4. display could be called or not, depending on repl.display
'''
VIEW_STACK_SIZE = 20
_view_writer = EUDByteRW()
_view_cnt = EUDVariable(0)
_view_stack = EUDArray(VIEW_STACK_SIZE)
_viewmem_stack = EUDArray(VIEW_STACK_SIZE)

def GetViewCount():
	return _view_cnt

@EUDFunc
def GetCurrentView():
	global _view_cnt, _view_stack, _viewmem_stack
	if EUDIf()(_view_cnt == 0):
		# f_raiseError("SC_REPL ERROR - GetCurrentView()")
		EUDReturn([0, 0])
	EUDEndIf()
	EUDReturn([_view_stack[_view_cnt-1], _viewmem_stack[_view_cnt-1]])

@EUDFunc
def TerminateCurrentView():
	global _view_cnt, _view_stack, _viewmem_stack
	if EUDIf()(_view_cnt == 0):
		f_raiseError("SC_REPL ERROR - TerminateTopView()")
	EUDEndIf()
	_view_cnt -= 1
	EUDView.cast(_view_stack[_view_cnt]).dest(_viewmem_stack[_view_cnt])

class EUDView(EUDStruct):
	_fields_ = [
		# arbitrary input,
		# output 0: EUDVArray pointer if success on contruct view
		#           otherwise 0
		('init', EUDFuncPtr(1, 1)),

		# keydown of keys are called
		# param 0: EUDVArray of members
		# param 1: Key code
		('keydown_callback', EUDFuncPtr(2, 0)),

		# All chat from superuser is processed into him
		# param 0: EUDVArray of members
		# param 1: chat pointer
		# If the view failed to understand, pass to REPL
		# return 1 if the view processed chat, otherwise 0
		('execute_chat', EUDFuncPtr(2, 1)),

		# If the view is on foreground, invoked every loop
		# update display in here!
		# param 0: EUDVArray of members
		# param 1: 1 if update of display needed
		('loop', EUDFuncPtr(1, 1)),

		# pointer to function that returns display buffer
		# param 0: EUDVArray of members
		# ret 0: EPD-Pointer of text buffer
		('get_bufepd', EUDFuncPtr(1, 1)),

		# pointer to destructor
		# param 0: EUDVArray of members
		('dest', EUDFuncPtr(1, 0)),
	]

	def __init__(self, init, keydown_callback, execute_chat,
			loop, get_bufepd, dest):
		super().__init__(_from = EUDVArray(6)([init, keydown_callback,
			execute_chat, loop, get_bufepd, dest]))

	@EUDMethod
	def OpenView(self, _in):
		global _view_stack, _viewmem_stack, _view_cnt
		mem = self.init(_in)
		if EUDIf()(mem != 0):
			# add
			_view_stack[_view_cnt] = self
			_viewmem_stack[_view_cnt] = mem
			_view_cnt += 1
		EUDEndIf()

