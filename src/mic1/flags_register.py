from src.components.signals import ISignalSender, SingleSignalSender
from src.utils.bit_utils import BitArray

class FlagsRegister:
    def __init__(self, in_n: ISignalSender, in_z: ISignalSender, in_cond: ISignalSender):
        self._in_n = in_n
        self._in_z = in_z
        self._in_cond = in_cond
        self._out = SingleSignalSender()

        self._in_n.signal_changed += self._update
        self._in_z.signal_changed += self._update
        self._in_cond.signal_changed += self._update

    @property
    def out_sig(self) -> ISignalSender: return self._out

    def _update(self, sender, _):
        self._out.disable()
        condition = self._in_cond.signal().to_int32()
        
        should_enable = False
        if condition == 1:
            should_enable = self._in_n.signal().has_all_set()
        elif condition == 2:
            should_enable = self._in_z.signal().has_all_set()
        elif condition == 3:
            should_enable = True
        
        if should_enable:
            self._out.enable()