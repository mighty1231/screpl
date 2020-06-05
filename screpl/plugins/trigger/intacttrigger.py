"""defines IntactTrigger"""

from eudplib import RawTrigger

class IntactTrigger(RawTrigger):
    """RawTrigger object that does not allow overlapping"""
    def WritePayload(self, pbuffer):
        pbuffer.WriteDword(self._prevptr)
        pbuffer.WriteDword(self._nextptr)

        # Conditions
        for cond in self._conditions:
            cond.WritePayload(pbuffer)

        if len(self._conditions) != 16:
            pbuffer.WriteBytes(bytes(20) * (16 - len(self._conditions)))

        # Actions
        for act in self._actions:
            act.WritePayload(pbuffer)

        if len(self._actions) != 64:
            pbuffer.WriteBytes(bytes(32) * (64 - len(self._actions)))

        # Preserved flag
        if self.preserved:
            pbuffer.WriteDword(4)
        else:
            pbuffer.WriteDword(0)

        pbuffer.WriteBytes(bytes(28))
