'''
Manager for all BridgeBlocks

struct Block {
    char signature[4];
    int size;
    char block[size]; // dynamic size
}

struct BridgeRegion {
    char signature[160];

    /* Too much milk solution #3, busy-waiting by A */
    int noteToSC;
    int noteFromSC;
    int regionSize;

    /* To SC */
    char command[300];

    /* From SC */
    int frameCount;

    DisplayBlock displayBlock;
    LogBlock logBlock;
    AppOutBlock appOutBlock;

    ...other blocks...
}

'''

from eudplib import *
from .block import BridgeBlock
from .signature import deadSign, f_restoreSign
from ..apps import Logger
from ..core import getAppManager

class BridgeRegion(EUDObject):
    _signature_ = b'BRID'

    def __init__(self):
        super().__init__()
        self.blocks = []

        self.off_noteToBridge   = self + 160
        self.off_noteFromBridge = self + 164
        self.off_regionSize     = self + 168
        self.off_command        = self + 172
        self.off_frameCount     = self + 472

        self.updater_forward = Forward()
        self.update_end = Forward()

    def AddBlock(self, block):
        assert isinstance(block, BridgeBlock)
        self.blocks.append(block)

        # modify UpdateContent
        PushTriggerScope()
        self.updater_forward << NextTrigger()
        block.UpdateContent()

        self.updater_forward = Forward()
        SetNextTrigger(self.updater_forward)
        PopTriggerScope()

    def UpdateContent(self):
        ############# from bridge ###############
        # read command
        if EUDIfNot()(Memory(region.off_command, Exactly, 0)):
            f_repmovsd_epd(EPD(buf_command), EPD(region.off_command), 300//4)

            # notify command is read
            DoActions(SetMemory(region.off_command, SetTo, 0))
        EUDEndIf()

        ############## to bridge ################
        # frame Count
        SeqCompute([
            (EPD(region.off_frameCount), SetTo, appManager.current_frame_number)
        ])

        # update blocks
        SetNextTrigger(self.updater_forward)
        self.update_end << NextTrigger()

    def Evaluate(self):
        # finalize UpdateContent
        self.updater_forward << self.update_end
        return super().Evaluate()

    def DynamicConstructed(self):
        return True

    def GetDataSize(self):
        size = 160 + 4*3 + 300 + 4
        for block in self.blocks:
            size += block.GetDataSize()
        return size

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteBytes(deadSign)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(self.GetDataSize())

        emitbuffer.WriteBytes(bytes(300))
        emitbuffer.WriteDword(0)

        for block in self.blocks:
            block.WritePayload(emitbuffer)

region = BridgeRegion()
buf_command = Db(300)

def bridge_init():
    Logger.format("Bridge shared region ptr = %H", EUDVariable(region))

def bridge_loop():
    appManager = getAppManager()

    # Too-much milk solution #3
    # attach note
    DoActions(SetMemory(region.off_noteToBridge, SetTo, 1))
    if EUDIf()(Memory(region.off_noteFromBridge, Exactly, 0)):
        # during note be attached, operations should be minimized
        region.UpdateContent()
    EUDEndIf()

    # remove note
    DoActions(SetMemory(region.off_noteToBridge, SetTo, 0))

    # keep signature (make bridge to know REPL is alive)
    f_restoreSign()

    # command from bridge client
    if EUDIfNot()(Memory(buf_command, Exactly, 0)):
        appManager.current_app_instance.onChat(buf_command)
        DoActions(SetMemory(buf_command, SetTo, 0))
    EUDEndIf()

