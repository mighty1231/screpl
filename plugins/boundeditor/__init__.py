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
g_obstacleunit = EUDVariable(EncodeUnit("Psi Emitter"))
g_start_location = EUDVariable(1)
g_runnerforce = EUDVariable(EncodePlayer(Force1))
g_runnerunit = EUDVariable(EncodeUnit("Zerg Zergling"))

TMODE_EUDTURBO = 0
TMODE_TURBO = 1
TMODE_NOTHING = 2
g_turbo_mode = EUDVariable(TMODE_EUDTURBO)

trigvalues = [0 for _ in range(2408)]
trigvalues[8+320+2048] = 4 # preserved trigger
g_emptyTrigger = Db(trigvalues)

# pattern variables
p_count = EUDVariable(1)
p_currentPattern = EUDVariable(0)
p_waitValue = EUDArray([1] * MAX_PATTERN_COUNT)
p_actionCount = EUDArray(MAX_PATTERN_COUNT)
p_actionArrayEPD = EUDArray([
    EPD(EUDArray(MAX_ACTION_COUNT * 32)) for _ in range(MAX_PATTERN_COUNT)
])

# pattern, detail
focused_pattern_id = EUDVariable(0)

@EUDFunc
def executePattern(pattern_id):
    cnt, action_epd = p_actionCount[pattern_id], p_actionArrayEPD[pattern_id]
    i = EUDVariable(0)
    i << 0
    if EUDInfLoop()():
        EUDBreakIf(i >= cnt)

        _nxttrig = Forward()

        # fill trigger
        DoActions(SetNextPtr(emptyTrigger, _nxttrig))
        f_repmovsd_epd(EPD(emptyTrigger + 8 + 320), action_epd, 32 // 4)

        # jump to trigger
        EUDJump(emptyTrigger)
        _nxttrig << NextTrigger()
        DoActions([
            i.AddNumber(1),
            action_epd.AddNumber(32 // 4)
        ])
    EUDEndInfLoop()

def cleanScreen():
    pass

# make commands
from .manager import BoundManagerApp

@AppCommand([])
def startCommand(self):
    appManager.startApplication(BoundManagerApp)

REPL.addCommand('bound', startCommand)
