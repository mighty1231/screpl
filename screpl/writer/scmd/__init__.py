from eudplib import *
from screpl.utils.referencetable import ReferenceTable
from screpl.utils.conststring import EPDConstString

def writer_scmd_init():
    from screpl.utils.byterw import REPLByteRW

    from screpl.writer.scmd.action import write_scmd_action
    from screpl.writer.scmd.action import write_scmd_action_epd
    from screpl.writer.scmd.condition import write_scmd_condition
    from screpl.writer.scmd.unit import write_scmd_unit

    REPLByteRW.add_method(write_scmd_unit)
    REPLByteRW.add_method(write_scmd_const)
    REPLByteRW.add_method(write_scmd_condition)
    REPLByteRW.add_method(write_scmd_action)
    REPLByteRW.add_method(write_scmd_action_epd)
    REPLByteRW.add_method(write_scmd_trigger)

def write_scmd_const(self, table, value):
    if IsEUDVariable(value):
        self.write_constant(EPD(table), value)
    else:
        key_tr = table.find_key_by_value(value)
        self.write_strepd(key_tr)

def write_scmd_trigger(self, player, conditions, actions, preserved=True):
    """write scmd trigger

    .. note::
        This is minimalized function to utilize for boundeditor plugin.
        So, there are many limitations, such as assigining trigger for
        more than one player.

    Args:
        player(int, EUDVariable): trigger player
        conditions(list): list of Condition
        actions(list, tuple): list of Action, or
            tuple of (# Actions, EUDArray of actions)
    """
    self.write_f("Trigger(")
    self.write_scmd_const(tb_scmd_player, player)

    self.write_f("){\nConditions:\n")
    for cond in conditions:
        if isinstance(cond, str):
            self.write_f(cond)
        elif isinstance(cond, tuple):
            self.write_f(*cond)
        elif isinstance(cond, Condition):
            self.write_scmd_condition(cond)
        else:
            raise RuntimeError("Unknown type condition {}".format(cond))

    self.write_f("\nActions:\n")

    if isinstance(actions, list):
        for act in actions:
            if isinstance(act, str):
                self.write_f(act)
            elif isinstance(act, tuple):
                self.write_f(*act)
            elif isinstance(act, Action):
                self.write_scmd_action(act)
            else:
                raise RuntimeError("Unknown type action {}".format(act))
    else:
        actcount, act_epd = actions

        cur_epd, end_epd = EUDVariable(), EUDVariable()
        cur_epd << act_epd
        end_epd << (act_epd + (32//4) * actcount)
        if EUDInfLoop()():
            EUDBreakIf(cur_epd >= end_epd)

            self.write_scmd_action_epd(cur_epd)
            cur_epd += (32//4)
        EUDEndInfLoop()

    if preserved:
        self.write_f("Preserve Trigger();\n")
    self.write_f("}\n\n")

tb_scmd_player = ReferenceTable([
    ('"Player 1"', Player1),
    ('"Player 2"', Player2),
    ('"Player 3"', Player3),
    ('"Player 4"', Player4),
    ('"Player 5"', Player5),
    ('"Player 6"', Player6),
    ('"Player 7"', Player7),
    ('"Player 8"', Player8),
    ('"Player 9"', Player9),
    ('"Player 10"', Player10),
    ('"Player 11"', Player11),
    ('"Player 12"', Player12),
    ('"Current Player"', CurrentPlayer),
    ('"Foes"', Foes),
    ('"Allies"', Allies),
    ('"Neutral Players"', NeutralPlayers),
    ('"All Players"', AllPlayers),
    ('"Force 1"', Force1),
    ('"Force 2"', Force2),
    ('"Force 3"', Force3),
    ('"Force 4"', Force4),
    ('"Non Allied Victory Players"', NonAlliedVictoryPlayers),
], key_f=EPDConstString, value_f=EncodePlayer, final=True)

tb_scmd_modifier = ReferenceTable([
    ("Set To", SetTo),
    ("Add", Add),
    ("Subtract", Subtract),
], key_f=EPDConstString, value_f=EncodeModifier, final=True)

tb_scmd_comparison = ReferenceTable([
    ("At least", AtLeast),
    ("At most", AtMost),
    ("Exactly", Exactly),
], key_f=EPDConstString, value_f=EncodeComparison, final=True)

tb_scmd_order = ReferenceTable([
    ("move", Move),
    ("patrol", Patrol),
    ("attack", Attack),
], key_f=EPDConstString, value_f=EncodeOrder, final=True)

tb_scmd_score = ReferenceTable([
    ("Total", Total),
    ("Units", Units),
    ("Buildings", Buildings),
    ("Units and buildings", UnitsAndBuildings),
    ("Kills", Kills),
    ("Razings", Razings),
    ("Kills and razings", KillsAndRazings),
    ("Custom", Custom),
], key_f=EPDConstString, value_f=EncodeScore, final=True)
