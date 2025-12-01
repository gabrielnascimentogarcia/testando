from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender

class Shifter:
    def __init__(self, input_sender: ISignalSender, in_control: ISignalSender):
        self._in = input_sender
        self._in_control = in_control
        self._in.signal_changed += self._update
        self._in_control.signal_changed += self._update
        self._out = SignalSender(len(self._in.signal()))

    @property
    def out_sig(self) -> ISignalSender: return self._out

    def _update(self, sender, _):
        input_bits = self._in.signal()
        control = self._in_control.signal().to_int32()
        
        if control == 1:
            result = input_bits.shift_left()
        elif control == 2:
            result = input_bits.shift_right()
        else:
            result = input_bits
        
        self._out.set_data(result)