from eudplib import *

from screpl.apps.repl import REPL
from screpl.main import get_app_manager
from screpl.core.appcommand import AppCommand

# initialize variables
app_manager = get_app_manager()
su_id = app_manager.get_superuser_id()

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
g_start_location = EUDVariable(1)
g_runner_force = EUDVariable(EncodePlayer(Force1))
g_runner_unit = EUDVariable(EncodeUnit("Zerg Zergling"))

OBSTACLE_CREATEPATTERN_KILL   = 0
OBSTACLE_CREATEPATTERN_REMOVE = 1
OBSTACLE_CREATEPATTERN_ALIVE  = 2
OBSTACLE_CREATEPATTERN_END    = 3
OBSTACLE_DESTRUCTPATTERN_KILL   = 0
OBSTACLE_DESTRUCTPATTERN_REMOVE = 1
OBSTACLE_DESTRUCTPATTERN_END    = 2

g_obstacle_unit = EUDVariable(EncodeUnit("Psi Emitter"))
g_obstacle_createpattern = EUDVariable(OBSTACLE_CREATEPATTERN_KILL)
g_obstacle_destructpattern = EUDVariable(OBSTACLE_DESTRUCTPATTERN_KILL)

TMODE_EUDTURBO = 0
TMODE_TURBO = 1
TMODE_NOTHING = 2
g_turbo_mode = EUDVariable(TMODE_EUDTURBO)

trigvalues = [0 for _ in range(2408)]
trigvalues[8+320+2048] = 4 # preserved trigger
g_empty_trigger = Db(trigvalues)

# pattern variables
p_count = EUDVariable(1)
p_wait_value = EUDArray([1] * MAX_PATTERN_COUNT)
p_action_count = EUDArray(MAX_PATTERN_COUNT)
p_action_array_epd = EUDArray([
    EPD(EUDArray(MAX_ACTION_COUNT * 32)) for _ in range(MAX_PATTERN_COUNT)
])

def write_player(self, value):
    from screpl.resources.table.tables import Player
    self.write_constant(EPD(Player), value)

# pattern, detail
focused_pattern_id = EUDVariable(0)

@EUDFunc
def execute_pattern(pattern_id):
    cnt, action_epd = p_action_count[pattern_id], p_action_array_epd[pattern_id]
    i = EUDVariable(0)
    i << 0
    if EUDInfLoop()():
        EUDBreakIf(i >= cnt)

        _nxttrig = Forward()

        # fill trigger
        DoActions(SetNextPtr(g_empty_trigger, _nxttrig))
        f_repmovsd_epd(EPD(g_empty_trigger + 8 + 320), action_epd, 32 // 4)

        # jump to trigger
        EUDJump(g_empty_trigger)
        _nxttrig << NextTrigger()
        DoActions([
            i.AddNumber(1),
            action_epd.AddNumber(32 // 4)
        ])
    EUDEndInfLoop()

def plugin_get_dependencies():
    # plugin dependencies
    return ['screpl.plugins.location', 'screpl.plugins.unit']

def plugin_setup():
    # make commands
    from .manager import BoundManagerApp

    @AppCommand([])
    def start_command(self):
        """Start BoundManagerApp"""
        app_manager.start_application(BoundManagerApp)

    REPL.add_command('bound', start_command)
