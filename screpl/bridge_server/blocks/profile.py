"""Defines ProfileBlock"""
from eudplib import *
from screpl.bridge_server import block
from screpl.monitor import profile_table

_buf = None

def get_block():
    global _buf
    if _buf is None:

        count = len(profile_table.table)
        base = 4 + 16 * count
        str_offsets = []
        str_table = bytes()

        # evaluate offsets for profile names
        for i in range(count):
            name = profile_table.table[i][0]
            str_offsets.append(base + len(str_table))
            str_table += name.encode('utf-8') + b'\x00'

        # construct buffer
        _buf = i2b4(count)
        for i in range(count):
            _buf += i2b4(str_offsets[i])
            _buf += bytes(12)
        _buf += str_table

        # padding for 4 byte aligning
        if len(_buf) % 4:
            _buf += bytes(4 - (len(_buf) % 4))
        assert len(_buf) % 4 == 0

    return _buf


class ProfileBlock(block.BridgeBlock):
    """Provides profiled results

    .. code-block:: C

        struct VariableEntry {
            int name_offset; // relative offset to ProfileBlock address
            int counter;
            int total_ms;
            int total_ticks;
        };

        struct ProfileBlock {
            int var_count;
            VariableEntry var_entries[var_count];
            char var_names[var_count]; // null-ended strings
        };
    """
    signature = b'PROF'

    def GetBufferSize(self):
        return len(get_block())

    def WritePayload(self, emitbuffer):
        buf_size = self.GetBufferSize()
        emitbuffer.WriteDword(b2i4(type(self).signature))
        emitbuffer.WriteDword(buf_size)
        emitbuffer.WriteBytes(get_block())

    def UpdateContent(self):
        computes = []
        for i, (name, counter, total_ms, total_ems) in \
                enumerate(profile_table.table):
            computes.append((EPD(self + i * 16 + 8), SetTo, counter))
            computes.append((EPD(self + i * 16 + 12), SetTo, total_ms))
            computes.append((EPD(self + i * 16 + 16), SetTo, total_ems))

        SeqCompute(computes)
