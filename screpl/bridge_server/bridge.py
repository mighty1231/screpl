"""Manages shared memory region with bridge client

Shared memory region has following structures

.. code-block:: C

    struct Block {
        char signature[4];
        int size;
        char block[size]; // dynamic size
    }

    struct BridgeRegion {
        char signature[160];

        /* Too much milk solution #3, busy-waiting by A */
        int note_to_bridge;
        int note_from_bridge;

        /* bridge protocol */
        int bridge_protocol;
        int region_size;

        /* To SC */
        char command[300];

        /* Heartbeat from SC */
        int inversed_system_millis;

        /* blocks */
        DisplayBlock display_block;
        LogBlock log_block;
        AppOutputBlock app_output_block;

        /* ...other blocks */
    }

"""
from eudplib import *

from screpl.apps.logger import Logger
from .blocks import (
    appoutput,
    blindmode,
    gametext,
    logger,
    profile,
)
from screpl.bridge_server.signature import dead_signature, restore_signature
import screpl.main as main

# protocol versions
BRIDGE_PROTOCOL_VER_1 = 0x20200604

class BridgeRegion(EUDObject):
    def __init__(self):
        super().__init__()
        self.blocks = []

        self._note_to_bridge = self + 160
        self._note_from_bridge = self + 164
        self._protocol = self + 168
        self._region_size = self + 172
        self._command = self + 176
        self._inversed_system_millis = self + 476

        self.blocks.append(appoutput.AppOutputBlock(self))
        self.blocks.append(blindmode.BlindModeDisplayBlock(self))
        self.blocks.append(gametext.GameTextBlock(self))
        self.blocks.append(logger.LoggerBlock(self))
        self.blocks.append(profile.ProfileBlock(self))

        # region_size is on region+160+4+4
        Logger.format("Bridge region ptr = %H, size = %D",
                      EUDVariable(self),
                      f_dwread_epd(EPD(self+160+4+4)))

    def Evaluate(self):
        ret = super().Evaluate()
        return ret

    def get_block_address(self, block):
        offset = 160 + 4*4 + 300 + 4
        for b in self.blocks:
            if b is block:
                return self.Evaluate() + offset
            offset += b.get_buffer_size() + 8
        raise RuntimeError

    def GetDataSize(self):
        size = 160 + 4*4 + 300 + 4
        for block in self.blocks:
            size += block.get_buffer_size() + 8
        return size

    def CollectDependency(self, emitbuffer):
        for block in self.blocks:
            block.collect_dependency(emitbuffer)

    def WritePayload(self, emitbuffer):
        emitbuffer.WriteBytes(dead_signature)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(0)
        emitbuffer.WriteDword(BRIDGE_PROTOCOL_VER_1)
        emitbuffer.WriteDword(self.GetDataSize())

        emitbuffer.WriteBytes(bytes(300))
        emitbuffer.WriteDword(0)

        for block in self.blocks:
            block.write_payload(emitbuffer)

    def run(self):
        """Maintains the instance"""
        buf_command = Db(300)

        # Too-much milk solution #3
        # attach note
        DoActions(SetMemory(self._note_to_bridge, SetTo, 1))
        if EUDIf()(Memory(self._note_from_bridge, Exactly, 0)):
            # during attached note, operations should be minimized

            ############# from bridge ###############
            # read command
            if EUDIfNot()(Memory(self._command, Exactly, 0)):
                f_repmovsd_epd(EPD(buf_command), EPD(self._command), 300//4)

                # notify command is read
                DoActions(SetMemory(self._command, SetTo, 0))
            EUDEndIf()

            ############## to bridge ################
            # heart beat
            f_dwwrite_epd(
                EPD(self._inversed_system_millis),
                f_dwread_epd(EPD(0x51CE8C)))

            # update blocks
            for b in self.blocks:
                b.update_content()
        EUDEndIf()

        # remove note
        DoActions(SetMemory(self._note_to_bridge, SetTo, 0))

        # keep signature (make bridge to know REPL is alive)
        restore_signature(self)

        # command from bridge client
        if EUDIfNot()(Memory(buf_command, Exactly, 0)):
            main.get_app_manager()              \
                .get_foreground_app_instance()  \
                .on_chat(buf_command)
            DoActions(SetMemory(buf_command, SetTo, 0))
        EUDEndIf()
