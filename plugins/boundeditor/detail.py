'''
feature
 * delete
 * modify
 * new
Expected TUI
 1. Pattern {pattern_id} actions, ESC to back
 2.  1. Create..
 3.  2. Kill..
 4.  3. ...
'''
from eudplib import *

from repl import Application, writeAction_epd
from . import appManager, focused_pattern_id, p_actionCount, p_actionArrayEPD

action_id = EUDVariable(0)
actionCount = EUDVariable(0)
actionArrayEPD = EUDVariable(0)

@EUDFunc
def focusActionID(new_actionid):
    if EUDIfNot()(new_actionid >= actionCount):
        if EUDIfNot()(new_actionid == action_id):
            action_id << new_actionid
            appManager.requestUpdate()
        EUDEndIf()
    EUDEndIf()

def deleteAction():
    global action_id
    if EUDIfNot()(actionCount == 0):
        cur_action_epd = actionArrayEPD + (32//4) * action_id
        next_action_epd = cur_action_epd + (32//4)
        _until_epd = actionArrayEPD + (32//4) * actionCount

        # overwrite
        if EUDInfLoop()():
            EUDBreakIf(next_action_epd == _until_epd)

            f_repmovsd_epd(cur_action_epd, next_action_epd, 32//4)

            DoActions([
                cur_action_epd.AddNumber(32//4),
                next_action_epd.AddNumber(32//4)
            ])
        EUDEndInfLoop()

        DoActions([
            actionCount.SubtractNumber(1),
            SetMemoryEPD(EPD(p_actionCount) + focused_pattern_id, Subtract, 1)
        ])

        if EUDIf()(action_id == actionCount):
            action_id -= 1
        EUDEndIf()
        appManager.requestUpdate()
    EUDEndIf()


class DetailedActionApp(Application):
    def onInit(self):
        actionCount << p_actionCount[focused_pattern_id]
        action_id << actionCount - 1
        actionArrayEPD << p_actionArrayEPD[focused_pattern_id]

    def loop(self):
        if EUDIf()(appManager.keyPress('ESC')):
            appManager.requestDestruct()
            EUDReturn()
        if EUDElseIf()(appManager.keyPress('f7')):
            focusActionID(action_id-1)
        if EUDElseIf()(appManager.keyPress('f8')):
            focusActionID(action_id+1)
        if EUDElseIf()(appManager.keyPress('delete')):
            deleteAction()
        EUDEndIf()

    def print(self, writer):
        writer.write_f("Pattern %D action editor, "\
                "press 'ESC' to go back\n", focused_pattern_id+1)

        branch, branch_common, branch_last = [Forward() for _ in range(3)]
        space = EUDVariable()
        quot, mod = f_div(action_id, 8)
        cur = quot * 8
        until = cur + 8
        if EUDIf()(until <= actionCount):
            DoActions(SetNextPtr(branch, branch_common))
        if EUDElse()():
            space << until - actionCount
            until << actionCount
            DoActions(SetNextPtr(branch, branch_last))
        EUDEndIf()

        # fill contents
        action_epd = actionArrayEPD + (32//4) * cur
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            if EUDIf()(cur == action_id):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            writer.write_f(" %D: ", cur)
            writeAction_epd(action_epd)
            writer.write(ord('\n'))

            DoActions([cur.AddNumber(1), action_epd.AddNumber(32//4)])
        EUDEndInfLoop()

        branch << RawTrigger()
        branch_last << NextTrigger()
        if EUDInfLoop()():
            EUDBreakIf(space == 0)
            writer.write(ord('\n'))
            space -= 1
        EUDEndInfLoop()

        branch_common << NextTrigger()
        writer.write(0)