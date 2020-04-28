from eudplib import *

from repl import REPL, getAppManager, AppCommand

# initialize variables
appManager = getAppManager()
superuser = appManager.superuser

computer_player_initvar = -1
for i in range(7, -1, -1):
    if GetPlayerInfo(i).typestr in ["Neutral", "Computer"]:
        computer_player_initvar = i
        break
if computer_player_initvar == -1:
    raise RuntimeError("Set 1 or more 'Computer' or 'Neutral' player")

MAX_PATTERN_COUNT = 50
MAX_ACTION_COUNT = 1000

g_effectplayer = EUDVariable(computer_player_initvar)
g_effectunit_1 = EUDVariable(EncodeUnit("Zerg Scourge"))
g_effectunit_2 = EUDVariable(EncodeUnit("Zerg Overlord"))
g_effectunit_3 = EUDVariable(EncodeUnit("Terran Battlecruiser"))
g_obstacle_unit = EUDVariable(EncodeUnit("Psi Emitter"))
g_start_location = EUDVariable(1)
g_end_location = EUDVariable(1)
g_runnerunit = EUDVariable(EncodeUnit("Zerg Zergling"))

TMODE_EUDTURBO = 0
TMODE_TURBO = 1
TMODE_NOTHING = 2
g_turbo_mode = EUDVariable(TMODE_EUDTURBO)

trigvalues = [0 for _ in range(2408)]
trigvalues[8+320+2048] = 4 # preserved trigger
g_emptyTrigger = Db(trigvalues)

# pattern variables
p_count = EUDVariable(0)
p_currentPattern = EUDVariable(-1)
p_waitValue = EUDArray(MAX_PATTERN_COUNT)
p_actionCount = EUDArray(MAX_PATTERN_COUNT)
p_actionArrayEPD = EUDArray([
    EPD(EUDArray(MAX_ACTION_COUNT * 32)) for _ in range(MAX_PATTERN_COUNT)
])

def lets_turbo():
    if EUDIf()(g_turbo_mode == 0):
        DoActions(SetMemory(0x6509A0, SetTo, 0))
    if EUDElseIf()(g_turbo_mode == 1):
        DoActions(SetMemory(0x6509A0, SetTo, 1))
    EUDEndIf()

# make commands
from .editor import BoundEditorApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(BoundEditorApp)

REPL.addCommand('bound', startCommand)
