from typing import Optional
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender, EventHandler

class Register:
    def __init__(self, length: int, 
                 data_sender: Optional[ISignalSender] = None, 
                 control_sender: Optional[ISignalSender] = None, 
                 name: Optional[str] = None):
        self.name = name
        self._out = SignalSender(length)
        self._in = None
        self._in_ctrl = None
        
        self.data_changed = EventHandler() # Event<BitArray>
        self.control_changed = EventHandler() # Event<bool>

        if data_sender: self.set_data_sender(data_sender)
        if control_sender: self.set_control_sender(control_sender)

    @property
    def out_sig(self) -> ISignalSender: return self._out

    def set_data_sender(self, data_sender: ISignalSender):
        self._in = data_sender

    def set_control_sender(self, control_sender: ISignalSender):
        if self._in_ctrl:
            self._in_ctrl.signal_changed -= self._on_control_change
        self._in_ctrl = control_sender
        self._in_ctrl.signal_changed += self._on_control_change

    def set_data(self, data: BitArray):
        self._out.set_data(data)
        if self.name:
            print(f"{self.name}, changed: {self._out.signal().to_bit_string()}")
        self.data_changed.invoke(self, self._out.signal())

    def reset(self):
        self.set_data(BitArray(len(self._out.signal()), False))

    def _on_control_change(self, sender, _):
        if self._in is None: return
        if self._in_ctrl.signal().has_all_set():
            self.set_data(self._in.signal())
            self.control_changed.invoke(self, True)
        else:
            self.control_changed.invoke(self, False)

    def __str__(self):
        return f"Register {self.name} ({self._out.signal().to_bit_string()})" if self.name else f"Register ({self._out.signal().to_bit_string()})"