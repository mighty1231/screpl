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
from .uuencode import uuencode, uudecode

_INTERACT_MAX = 6

class SyncLimitError(Exception):
    pass

class SyncManager:
    def __init__(self, su_id, is_multiplaying):
        self.su_id = su_id
        self.is_multiplaying = is_multiplaying

        # https://github.com/phu54321/vgce/blob/master/docs/Blizzard/Starcraft/packets2.txt#L17
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
        self._send_variables = [EUDVariable() for _ in range(_INTERACT_MAX)]
        self._send_variable_epds = [EUDVariable() for _ in range(_INTERACT_MAX)]


    @EUDMethod
    def _sync_and_check(self, size, funcptr, epdvals, comptypes, compvals):
        cond_comp0 = [Forward() for _ in range(_INTERACT_MAX)]
        cond_comp1 = [Forward() for _ in range(_INTERACT_MAX)]
        trig_preproc_end = Forward()
        trig_branch = Forward()
        trig_ifthen = Forward()
        trig_finally = Forward()

        v_ret_bool = EUDVariable()

        f_readcomptype_epd = f_readgen_epd(0x0F0B0000, (0, lambda t: t))

        epdval_variables = []
        for i in range(_INTERACT_MAX):
            if EUDIf()(MemoryEPD(epdvals + i, Exactly, 0)):
                # make action 0
                SeqCompute([
                    (EPD(cond_comp0[i]+12), SetTo, 0),
                    (EPD(cond_comp1[i]+12), SetTo, 0),
                ])
                EUDJump(trig_preproc_end)
            EUDEndIf()
            epdval = f_dwread_epd(epdvals + i)
            comptype = f_readcomptype_epd(comptypes+i)
            compval = f_dwread_epd(compvals + i)

            epdval_variables.append(epdval)

            SeqCompute([
                (EPD(cond_comp0[i]+4), SetTo, epdval),
                (EPD(cond_comp0[i]+12), SetTo, comptype),
                (EPD(cond_comp0[i]+8), SetTo, compval),

                (EPD(cond_comp1[i]+12), SetTo, comptype),
                (EPD(cond_comp1[i]+8), SetTo, compval),
            ])
        trig_preproc_end << NextTrigger()

        if EUDIf()([cond << MemoryEPD(0, Exactly, 0)
                    for cond in cond_comp0]):
            DoActions(SetNextPtr(trig_branch, trig_ifthen))
            v_ret_bool << 1
        if EUDElse()():
            DoActions(SetNextPtr(trig_branch, trig_finally))
            v_ret_bool << 0
        EUDEndIf()

        if EUDIf()(self.is_multiplaying()):
            trig_branch << RawTrigger()
            trig_ifthen << NextTrigger()

            # send superuser's memory status
            if EUDIf()(Memory(0x512684, Exactly, self.su_id)):
                # fill buffer
                trig_cond_end, trig_write_end = Forward(), Forward()
                v_buffer_epdaddrs, v_buffer_values = EUDVariable(), EUDVariable()

                SeqCompute([(EPD(self.buffer), SetTo, funcptr)])

                # loop epd / values
                v_buffer_epdaddrs << self.epdaddrs
                v_buffer_values << self.values
                for i, epdval in enumerate(epdval_variables):
                    EUDJumpIf(MemoryEPD(epdvals + i, Exactly, 0), trig_cond_end)
                    f_dwwrite_epd(v_buffer_epdaddrs, epdval)
                    f_dwwrite_epd(v_buffer_values, f_dwread_epd(epdval))
                    DoActions([
                        v_buffer_epdaddrs.AddNumber(1),
                        v_buffer_values.AddNumber(1),
                    ])
                trig_cond_end << NextTrigger()

                # loop over sending variables
                for var, var_epd in zip(self._send_variables,
                                        self._send_variable_epds):
                    EUDJumpIf(var_epd.Exactly(0), trig_write_end)
                    f_dwwrite_epd(v_buffer_epdaddrs, var_epd)
                    f_dwwrite_epd(v_buffer_values, var)
                    DoActions([
                        v_buffer_epdaddrs.AddNumber(1),
                        v_buffer_values.AddNumber(1),
                    ])
                trig_write_end << NextTrigger()

                # make endpoint
                if EUDIfNot()(size == _INTERACT_MAX):
                    f_dwwrite_epd(self.epdaddrs + size, 0)
                EUDEndIf()

                uuencode(self.buffer,
                         4 * (1 + _INTERACT_MAX + size),
                         EPD(self.gc_buffer) + 2)
                QueueGameCommand(self.gc_buffer + 2, 82)
            EUDEndIf()

            trig_finally << NextTrigger()

            # check condition with sync
            trig_break = Forward()
            match_success = Forward()
            match_fail = Forward()
            match_end = Forward()

            if EUDIfNot()(Memory(self.recv_buffer, Exactly, funcptr)):
                EUDJump(match_fail)
            EUDEndIf()

            # check conditions
            for i, epdval in enumerate(epdval_variables):
                EUDJumpIf(MemoryEPD(epdvals + i, Exactly, 0), trig_break)
                self.search_epd(epdval)
                if EUDIfNot()(self._search_success):
                    EUDJump(match_fail)
                EUDEndIf()
                if EUDIfNot()((cond_comp1[i]
                               << MemoryEPD(self._searched_value_epdp,
                                            Exactly, 0))):
                    EUDJump(match_fail)
                EUDEndIf()

            trig_break << NextTrigger()

            # set variables
            for epdval in self._send_variable_epds:
                EUDJumpIf(epdval == 0, match_success)
                self.search_epd(epdval)
                if EUDIf()(self._search_success):
                    f_dwwrite_epd(epdval,
                                  f_dwread_epd(self._searched_value_epdp))
                EUDEndIf()

            match_success << NextTrigger()
            v_ret_bool << 1
            EUDJump(match_end)

            match_fail << NextTrigger()
            v_ret_bool << 0
            match_end << NextTrigger()
        EUDEndIf()

        return v_ret_bool

    def sync_and_check(self, method, condition_pairs, sync=[]):
        """Send private memory of superuser and check the condition met

        Args:
            sync(list): list of EUDVariables to synchronize
        """
        if not method:
            raise RuntimeError(
                "User interactions should be checked under "
                "interactive AppMethods, method:{}"
                .format(method))

        size = len(condition_pairs) + len(sync)
        if size > _INTERACT_MAX:
            raise SyncLimitError()

        epds, comptypes, values = [], [], []
        for epd, comptype, value in condition_pairs:
            epds.append(epd)
            comptypes.append((EncodeComparison(comptype) << 16) + 0xf000000)
            values.append(value)
        epds.extend([0] * (_INTERACT_MAX - len(condition_pairs)))
        comptypes.extend([0] * (_INTERACT_MAX - len(condition_pairs)))
        values.extend([0] * (_INTERACT_MAX - len(condition_pairs)))

        for i, var in enumerate(sync):
            self._send_variables[i] << var
            self._send_variable_epds[i] << EPD(var.getValueAddr())
        if len(sync) < _INTERACT_MAX:
            self._send_variable_epds[len(sync)] << 0

        return self._sync_and_check(size, method.funcptr,
            EPD(EUDArray(epds)), EPD(EUDArray(comptypes)), EPD(EUDArray(values)))


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
        if EUDIf()(Memory(self.recv_buffer, Exactly, 0)):
            if EUDIf()(f_memcmp(address, Db(b'\x14SCR'), 4) == 0):
                written = uudecode(address + 4, EPD(self.recv_buffer))
                f_bwrite(address, 0)
            EUDEndIf()
        EUDEndIf()

    def log_buffer(self, title, buf):
        from screpl.apps.logger import Logger
        with Logger.get_multiline_writer(title) as writer:
            writer.write_f("funcptr %H\n", f_dwread_epd(EPD(buf)))
            for i in range(_INTERACT_MAX):
                epd = f_dwread_epd(EPD(buf) + 1 + i)
                value = f_dwread_epd(EPD(buf) + 1 + i + _INTERACT_MAX)
                writer.write_f(" %D: %H: %D\n", i, 0x58A364+4*epd, value)
            writer.write(0)
