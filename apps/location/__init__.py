from repl import REPL, getAppManager, AppCommand, EUDByteRW
from .locapp import LocationApp

@AppCommand([])
def openingCommand(self):
    '''
    At here, 'self' will become REPL instance
    The codes after openApplication are not executed
    '''
    getAppManager().openApplication(LocationApp)

REPL.addCommand('openloc', openingCommand)
