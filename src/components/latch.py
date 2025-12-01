from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender, EventHandler

class Latch:
    def __init__(self, data_sender: ISignalSender, control_sender: ISignalSender):
        self._output_enabled = False
        self._in = None
        self._in_ctrl = None
        self._out = SignalSender(len(data_sender.signal()))
        self.ew_changed = EventHandler() # Event<bool>

        self.set_data_sender(data_sender)
        self.set_control_sender(control_sender)

    @property
    def out_sig(self) -> ISignalSender: return self._out
    @property
    def output_enabled(self) -> bool: return self._output_enabled

    def reset(self):
        self._out.set_data(BitArray(len(self._out.signal()), False))

    def set_data_sender(self, data_sender: ISignalSender):
        if self._in is not None:
            self._in.signal_changed -= self._on_data_change
        self._in = data_sender
        self._in.signal_changed += self._on_data_change

    def set_control_sender(self, control_sender: ISignalSender):
        if self._in_ctrl is not None:
            self._in_ctrl.signal_changed -= self._on_control_change
        self._in_ctrl = control_sender
        self._in_ctrl.signal_changed += self._on_control_change
        self._on_control_change(control_sender, control_sender.signal())

    def _on_data_change(self, sender, _):
        if self._in is None or not self._output_enabled: return
        self._out.set_data(self._in.signal())

    def _on_control_change(self, sender, _):
        self._output_enabled = self._in_ctrl.signal().has_all_set()
        if self._in is None or not self._output_enabled: return
        self._out.set_data(self._in.signal())