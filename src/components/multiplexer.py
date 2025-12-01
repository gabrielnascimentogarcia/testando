from typing import List
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender

class Multiplexer:
    def __init__(self, length: int, input_senders: List[ISignalSender], control_sender: ISignalSender):
        self._in = input_senders
        self._in_ctrl = control_sender
        self._in_ctrl.signal_changed += self._on_control_change
        
        index = self._in_ctrl.signal().to_int32()
        self._current = self._in[index]
        self._current.signal_changed += self._on_current_change

        self._out = SignalSender(length)
        self._out.set_data(self._current.signal())

    @property
    def out_sig(self) -> ISignalSender: return self._out

    def set_output(self, index: int):
        self._current.signal_changed -= self._on_current_change
        self._current = self._in[index]
        self._current.signal_changed += self._on_current_change
        self._out.set_data(self._current.signal())

    def _on_control_change(self, sender, _):
        index = self._in_ctrl.signal().to_int32()
        self.set_output(index)

    def _on_current_change(self, sender, _):
        self._out.set_data(self._current.signal())