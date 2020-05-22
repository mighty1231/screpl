"""Manages shared memory region with bridge client

Shared memory region has following structures

.. code-block: C

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

        /* blocks */
        DisplayBlock displayBlock;
        LogBlock logBlock;
        AppOutBlock appOutBlock;

        /* ...other blocks */
    }

"""
from eudplib import *

from repl.apps.logger import Logger
from repl.bridge_server.blocks import appoutput
from repl.bridge_server.blocks import blindmode
from repl.bridge_server.blocks import gametext
from repl.bridge_server.blocks import logger
from repl.bridge_server.blocks import profile
from repl.bridge_server.signature import dead_signature, RestoreSignature
import repl.main as main

class BridgeRegion(EUDObject):
    def __init__(self):
        super().__init__()
        self.blocks = []

        self._noteToBridge   = self + 160
        self._noteFromBridge = self + 164
        self._regionSize     = self + 168
        self._command        = self + 172
        self._frameCount     = self + 472

        self.blocks.append(appoutput.AppOutputBlock(self))
        self.blocks.append(blindmode.BlindModeDisplayBlock(self))
        self.blocks.append(gametext.GameTextBlock(self))
        self.blocks.append(logger.LoggerBlock(self))
        self.blocks.append(profile.ProfileBlock(self))

        # regionSize is on region+160+4+4
        Logger.format("Bridge region ptr = %H, size = %D",
                      EUDVariable(self),
                      f_dwread_epd(EPD(self+160+4+4)))

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
        emitbuffer.WriteBytes(dead_signature)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(self.GetDataSize())

        emitbuffer.WriteBytes(bytes(300))
        emitbuffer.WriteDword(0)

        for block in self.blocks:
            block.WritePayload(emitbuffer)

    def run(self):
        """Maintains the instance"""
        buf_command = Db(300)

        # Too-much milk solution #3
        # attach note
        DoActions(SetMemory(self._noteToBridge, SetTo, 1))
        if EUDIf()(Memory(self._noteFromBridge, Exactly, 0)):
            # during attached note, operations should be minimized

            ############# from bridge ###############
            # read command
            if EUDIfNot()(Memory(region._command, Exactly, 0)):
                f_repmovsd_epd(EPD(buf_command), EPD(region._command), 300//4)

                # notify command is read
                DoActions(SetMemory(region._command, SetTo, 0))
            EUDEndIf()

            ############## to bridge ################
            # frame Count
            SeqCompute([(EPD(region._frameCount),
                         SetTo,
                         main.get_app_manager().current_frame_number)])

            # update blocks
            for b in self.blocks:
                b.UpdateContent()
        EUDEndIf()

        # remove note
        DoActions(SetMemory(self._noteToBridge, SetTo, 0))

        # keep signature (make bridge to know REPL is alive)
        RestoreSignature(self)

        # command from bridge client
        if EUDIfNot()(Memory(buf_command, Exactly, 0)):
            main.get_app_manager().getCurrentAppInstance().onChat(buf_command)
            DoActions(SetMemory(buf_command, SetTo, 0))
        EUDEndIf()
