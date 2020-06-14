"""Synchronize private memory

.. code-block:: c

    struct interaction {
        int signature; // \x14SCR
        char encoded_content[76];
    };

    // rate 0.75 (uuencode)
    // 76 * (0.75) = 57
    struct decoded_content {
        int method_id;
        int epdaddrs[6];
        int values[6];
    };

"""
from eudplib import *
from .struct import REPLStruct
from .uuencode import uuencode, uudecode

_INTERACT_MAX = 6

class SyncLimitError(Exception):
    pass

class SyncManager:
    def __init__(self, su_id, is_multiplaying):
        self.su_id = su_id
        self.is_multiplaying = is_multiplaying
        self.gc_buffer = Db(b'..\x5C\xFF\x14SCR' + b'.' * 76)
        self.buffer = EUDArray(_INTERACT_MAX * 2 + 1)
        self.epdaddrs = EPD(self.buffer) + 1
        self.values = EPD(self.buffer) + 1 + _INTERACT_MAX

        # received
        self.recv_buffer = EUDArray(_INTERACT_MAX * 2 + 1)
        self.recv_epdaddrs = EPD(self.buffer) + 1
        self.recv_values = EPD(self.buffer) + 1 + _INTERACT_MAX

        self._search_success = EUDVariable()
        self._searched_value_epdp = EUDVariable()

    def interact_check(self,
                       method,
                       condition_pairs,
                       send_variables=[]):
        """Send private memory of superuser and check the condition met"""
        conditions = []
        for epd, condfunc in condition_pairs:
            conditions.append(condfunc(epd))

        size = len(condition_pairs) + len(send_variables)
        if size > _INTERACT_MAX:
            raise SyncLimitError()

        v_ret_bool = EUDVariable()
        trig_branch = Forward()
        trig_ifthen = Forward()
        trig_finally = Forward()
        if EUDIf()(conditions):
            DoActions(SetNextPtr(trig_branch, trig_ifthen))
            v_ret_bool << 1
        if EUDElse()():
            DoActions(SetNextPtr(trig_branch, trig_finally))
            v_ret_bool << 0
        EUDEndIf()

        if EUDIf()(self.is_multiplaying()):
            trig_branch << RawTrigger()
            trig_ifthen << NextTrigger()

            assign_epds = []
            assign_values = []
            for epd, _ in condition_pairs:
                assign_epds.append((self.epdaddrs + len(assign_epds),
                                    SetTo,
                                    epd))
                assign_values.append((
                    self.values + len(assign_values),
                    SetTo,
                    f_dwread_epd(self.epdaddrs + len(assign_epds))))

            for var in send_variables:
                assign_epds.append((self.epdaddrs + len(assign_epds),
                                    SetTo,
                                    EPD(var.getValueAddr())))
                assign_values.append((self.values + len(assign_values),
                                      SetTo,
                                      var))

            if len(assign_epds) < _INTERACT_MAX:
                assign_epds.append((self.epdaddrs + len(assign_epds),
                                    SetTo, 0))

            # send superuser's memory status
            if EUDIf()(Memory(0x512684, Exactly, self.su_id)):
                SeqCompute([(EPD(self.buffer), SetTo, method.funcptr)]
                           + assign_epds + assign_values)
                uuencode(self.buffer,
                         4 * (1 + _INTERACT_MAX + size),
                         EPD(self.gc_buffer) + 2)
                QueueGameCommand(self.gc_buffer + 2, 82)
            EUDEndIf()

            trig_finally << NextTrigger()

            # check condition with sync
            match_success = Forward()
            match_fail = Forward()
            match_end = Forward()

            if EUDIfNot()(Memory(self.recv_buffer, Exactly, method.funcptr)):
                EUDJump(match_fail)
            EUDEndIf()

            # check conditions
            for epd, condfunc in condition_pairs:
                self.search_epd(epd)
                if EUDIfNot()(self._search_success):
                    EUDJump(match_fail)
                EUDEndIf()
                if EUDIfNot()(condfunc(self._searched_value_epdp)):
                    EUDJump(match_fail)
                EUDEndIf()

            # set variables
            for var in send_variables:
                self.search_epd(EPD(var.getValueAddr()))
                if EUDIf()(self._search_success):
                    var << f_dwread_epd(self._searched_value_epdp)
                EUDEndIf()

            v_ret_bool << 1
            EUDJump(match_end)

            match_fail << NextTrigger()
            v_ret_bool << 0
            match_end << NextTrigger()
        EUDEndIf()

        return v_ret_bool == 1

    @EUDMethod
    def search_epd(self, epdv):
        trig_comp = Forward()
        trig_comp2 = Forward()
        epdaddrp = EUDVariable()

        SeqCompute([
            (self._search_success, SetTo, 0),
            (self._searched_value_epdp, SetTo, self.recv_values),
            (EPD(trig_comp + 4), SetTo, self.recv_epdaddrs),
            (EPD(trig_comp + 8), SetTo, epdv),
            (EPD(trig_comp2 + 4), SetTo, self.recv_epdaddrs),
        ])

        if EUDLoopN()(_INTERACT_MAX):
            # if *addrepdp == epdv
            if EUDIf()(trig_comp << Memory(0, Exactly, 0)):
                self._search_success << 1
                EUDReturn()
            EUDEndIf()

            # if *addrepdp == 0
            if EUDIf()(trig_comp2 << Memory(0, Exactly, 0)):
                EUDBreak()
            EUDEndIf()

            SeqCompute([
                (EPD(trig_comp + 4), Add, 1),
                (EPD(trig_comp2 + 4), Add, 1),
                (self._searched_value_epdp, Add, 1),
            ])
        EUDEndLoopN()

    def clear_recv(self):
        self.recv_buffer[0] = 0

    def parse_recv(self, address):
        if EUDIf()(f_memcmp(address, Db(b'\x14SCR'), 4) == 0):
            written = uudecode(address + 4, EPD(self.recv_buffer))
            f_bwrite(address, 0)
        EUDEndIf()
