from repl import REPL, getAppManager, AppCommand, EUDByteRW
from .locapp import LocationApp

@AppCommand([])
def startCommand(self):
    '''
    At here, 'self' will become REPL instance
    The codes after startApplication are not executed
    '''
    getAppManager().startApplication(LocationApp)

REPL.addCommand('location', startCommand)
