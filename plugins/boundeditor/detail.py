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

from repl import Application
from . import appManager, focused_pattern_id

action_id = EUDVariable(0)
actionCount = EUDVariable(0)
actionArrayEPD = EUDVariable(0)

@EUDFunc
def focusActionID(new_actionid):
    if EUDIf()(new_actionid <= actionCount):
        if EUDIfNot()(new_actionid == action_id):
            action_id = new_actionid
            appManager.requestUpdate()
        EUDEndIf()
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
        written_point = Forward()
        if EUDInfLoop()():
            EUDBreakIf(cur >= until)

            if EUDIf()(cur == action_id):
                writer.write(0x11) # orange
            if EUDElse()():
                writer.write(0x02) # pale blue
            EUDEndIf()

            writer.write_f(" %D: ", cur)

            
            if EUDIf()(cur <= 227):
                stringid = off_unitsdat_UnitMapString.read(cur)

                if EUDIfNot()(stringid == 0):
                    writer.write_STR_string(stringid)
                    EUDJump(written_point)
                EUDEndIf()
            EUDEndIf()
            writer.write_f("%E", EUDGetDefaultUnitName_epd(cur))

            written_point << NextTrigger()
            writer.write(ord('\n'))

            DoActions(cur.AddNumber(1))
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