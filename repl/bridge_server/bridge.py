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

    def AddBlock(self, blockcls):
        assert issubclass(blockcls, BridgeBlock)
        block = blockcls(self)
        self.blocks.append(block)

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
            (EPD(region.off_frameCount), SetTo, getAppManager().current_frame_number)
        ])

        # update blocks
        for b in self.blocks:
            b.UpdateContent()

    def Evaluate(self):
        ret = super().Evaluate()
        return ret

    def GetBlockAddr(self, block):
        offset = 160 + 4*3 + 300 + 4
        for b in self.blocks:
            if b is block:
                return self.Evaluate() + offset
            offset += b.GetBufferSize() + 8
        raise RuntimeError

    def GetDataSize(self):
        size = 160 + 4*3 + 300 + 4
        for block in self.blocks:
            size += block.GetBufferSize() + 8
        return size

    def CollectDependency(self, emitbuffer):
        for block in self.blocks:
            block.CollectDependency(emitbuffer)

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
    from .gametext import GameTextBlock
    from .blindmode import BlindModeDisplayBlock
    from .logger import LoggerBlock
    from .appoutput import AppOutputBlock

    region.AddBlock(GameTextBlock)
    region.AddBlock(LoggerBlock)
    region.AddBlock(AppOutputBlock)
    region.AddBlock(BlindModeDisplayBlock)

    Logger.format("Bridge region ptr = %H, size = %D",
        EUDVariable(region),
        f_dwread_epd(EPD(region + 160 + 4 + 4))
    )

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
    f_restoreSign(region)

    # command from bridge client
    if EUDIfNot()(Memory(buf_command, Exactly, 0)):
        appManager.current_app_instance.onChat(buf_command)
        DoActions(SetMemory(buf_command, SetTo, 0))
    EUDEndIf()

