from eudplib import *
from screpl.main import get_main_writer

def make_scmd_const_writer(encoder, kvmap):
    @EUDFunc
    def writeVar(var):
        for i, (k, v) in enumerate(kvmap):
            _br = EUDIf if i == 0 else EUDElseIf
            _br()(var.Exactly(encoder(k)))
            get_main_writer().write_f(v)
        EUDElse()()
        get_main_writer().write_decimal(var)
        EUDEndIf()

    def write(value):
        if IsEUDVariable(value):
            writeVar(value)
        else:
            for k, v in kvmap:
                if encoder(k) == encoder(value):
                    get_main_writer().write_f(v)
                    return
            get_main_writer().write_decimal(encoder(value))

    return write

def write_scmd_number(value):
    if IsEUDVariable(value):
        get_main_writer().write_decimal(value)
    else:
        get_main_writer().write_f(str(value))

def write_scmd_trigger(player, conditions, actions, preserved=True):
    from .condition import write_scmd_condition
    from .action import write_scmd_action, write_scmd_action_epd
    '''
    actions = [SetDeaths(~~), SetDeaths(~~), ...]
    or
    actions = (EUDVariable(2), action_array_epd)
    '''

    get_main_writer().write_f("Trigger(")
    write_scmd_player(player)

    get_main_writer().write_f("){\nConditions:\n")
    for cond in conditions:
        if isinstance(cond, str):
            get_main_writer().write_f(cond)
        elif isinstance(cond, tuple):
            get_main_writer().write_f(*cond)
        elif isinstance(cond, Condition):
            write_scmd_condition(cond)
        else:
            raise RuntimeError("Unknown type condition {}".format(cond))

    get_main_writer().write_f("\nActions:\n")

    if isinstance(actions, list):
        for act in actions:
            if isinstance(act, str):
                get_main_writer().write_f(act)
            elif isinstance(act, tuple):
                get_main_writer().write_f(*act)
            elif isinstance(act, Action):
                write_scmd_action(act)
            else:
                raise RuntimeError("Unknown type action {}".format(act))
    else:
        actcount, act_epd = actions

        cur_epd, end_epd = EUDVariable(), EUDVariable()
        cur_epd << act_epd
        end_epd << (act_epd + (32//4) * actcount)
        if EUDInfLoop()():
            EUDBreakIf(cur_epd >= end_epd)

            write_scmd_action_epd(cur_epd)
            cur_epd += (32//4)
        EUDEndInfLoop()

    if preserved:
        get_main_writer().write_f("Preserve Trigger();\n")
    get_main_writer().write_f("}\n\n")


write_scmd_player = make_scmd_const_writer(EncodePlayer, [
    (Player1, "\"Player 1\""),
    (Player2, "\"Player 2\""),
    (Player3, "\"Player 3\""),
    (Player4, "\"Player 4\""),
    (Player5, "\"Player 5\""),
    (Player6, "\"Player 6\""),
    (Player7, "\"Player 7\""),
    (Player8, "\"Player 8\""),
    (Player12, "\"Player 12\""),
    (Force1, "\"Force 1\""),
    (Force2, "\"Force 2\""),
    (Force3, "\"Force 3\""),
    (Force4, "\"Force 4\""),
    (AllPlayers, "\"All Players\""),
    (CurrentPlayer, "\"Current Player\""),
])

write_scmd_modifier = make_scmd_const_writer(EncodeModifier, [
    (SetTo, "Set To"),
    (Add, "Add"),
    (Subtract, "Subtract")
])

write_scmd_comparison = make_scmd_const_writer(EncodeComparison, [
    (AtLeast, "At least"),
    (AtMost, "At most"),
    (Exactly, "Exactly"),
])

write_scmd_order = make_scmd_const_writer(EncodeOrder, [
    (Move, "move"),
    (Patrol, "patrol"),
    (Attack, "attack"),
])

write_scmd_score = make_scmd_const_writer(EncodeScore, [
    (Total, "Total"),
    (Units, "Units"),
    (Buildings, "Buildings"),
    (UnitsAndBuildings, "Units and buildings"),
    (Kills, "Kills"),
    (Razings, "Razings"),
    (KillsAndRazings, "Kills and razings"),
    (Custom, "Custom"),
])
