from eudplib import *

_writer = None
def getWriter():
    global _writer
    if _writer is None:
        from ...core import getAppManager
        _writer = getAppManager().getWriter()
    return _writer

def makeSCMDConstWriter(encoder, kvmap):
    @EUDFunc
    def writeVar(var):
        for i, (k, v) in enumerate(kvmap):
            _br = EUDIf if i == 0 else EUDElseIf
            _br()(var.Exactly(encoder(k)))
            getWriter().write_f(v)
        EUDElse()()
        getWriter().write_decimal(var)
        EUDEndIf()

    def write(value):
        if IsEUDVariable(value):
            writeVar(value)
        else:
            for k, v in kvmap:
                if encoder(k) == encoder(value):
                    getWriter().write_f(v)
                    return
            getWriter().write_decimal(encoder(value))

    return write

def SCMDWriteNumber(value):
    if IsEUDVariable(value):
        getWriter().write_decimal(value)
    else:
        getWriter().write_f(str(value))

def writeTrigger(player, conditions, actions, preserved = True):
    from .condition import SCMDWriteCondition
    from .action import SCMDWriteAction, SCMDWriteAction_epd
    '''
    actions = [SetDeaths(~~), SetDeaths(~~), ...]
    or
    actions = (EUDVariable(2), action_array_epd)
    '''

    getWriter().write_f("Trigger(")
    SCMDWritePlayer(player)

    getWriter().write_f("){\nConditions:\n")
    for cond in conditions:
        if type(cond) == str:
            getWriter().write_f(cond)
        elif type(cond) == tuple:
            getWriter().write_f(*cond)
        elif type(cond) == Condition:
            SCMDWriteCondition(cond)
        else:
            raise RuntimeError("Unknown type condition {}".format(cond))

    getWriter().write_f("\nActions:\n")

    from repl import f_raiseWarning
    f_raiseWarning("Writing actions..")

    if isinstance(actions, list):
        for act in actions:
            if type(act) == str:
                getWriter().write_f(act)
            elif type(act) == tuple:
                getWriter().write_f(*act)
            elif type(act) == Action:
                SCMDWriteAction(act)
            else:
                raise RuntimeError("Unknown type action {}".format(act))
    else:
        actcount, act_epd = actions

        cur_epd, end_epd = EUDVariable(), EUDVariable()
        cur_epd << act_epd
        end_epd << (act_epd + (32//4) * actcount)
        if EUDInfLoop()():
            EUDBreakIf(cur_epd >= end_epd)

            SCMDWriteAction_epd(cur_epd)
            cur_epd += (32//4)
        EUDEndInfLoop()

    from repl import f_raiseWarning
    f_raiseWarning("Writing actions.. done!")

    if preserved:
        getWriter().write_f("Preserve Trigger();\n")
    getWriter().write_f("}\n\n")


SCMDWritePlayer = makeSCMDConstWriter(EncodePlayer, [
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

SCMDWriteModifier = makeSCMDConstWriter(EncodeModifier, [
    (SetTo, "Set To"),
    (Add, "Add"),
    (Subtract, "Subtract")
])

SCMDWriteComparison = makeSCMDConstWriter(EncodeComparison, [
    (AtLeast, "At least"),
    (AtMost, "At most"),
    (Exactly, "Exactly"),
])

SCMDWriteOrder = makeSCMDConstWriter(EncodeOrder, [
    (Move, "move"),
    (Patrol, "patrol"),
    (Attack, "attack"),
])

SCMDWriteScore = makeSCMDConstWriter(EncodeScore, [
    (Total, "Total"),
    (Units, "Units"),
    (Buildings, "Buildings"),
    (UnitsAndBuildings, "Units and buildings"),
    (Kills, "Kills"),
    (Razings, "Razings"),
    (KillsAndRazings, "Kills and razings"),
    (Custom, "Custom"),
])
