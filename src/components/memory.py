from typing import List, Optional
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender, EventHandler
from src.components.clock import Clock

class Memory:
    def __init__(self, length: int, cell_length: int, 
                 address_sender: ISignalSender, in_buffer_sender: ISignalSender,
                 rd_sender: Optional[ISignalSender], wr_sender: Optional[ISignalSender],
                 name: Optional[str] = None):
        
        self._cells = [BitArray(cell_length) for _ in range(length)]
        self._cell_length = cell_length
        self._in_address = address_sender
        self._in_buffer = in_buffer_sender
        self._in_rd = rd_sender
        self._in_wr = wr_sender
        self.name = name
        self._out = SignalSender(cell_length)

        self.cell_changed = EventHandler() # Event<int>
        self.resetted = EventHandler()

        if self._in_rd: self._in_rd.signal_changed += self._on_rd_signal_changed
        if self._in_wr: self._in_wr.signal_changed += self._on_wr_signal_changed

    @property
    def out_sig(self) -> ISignalSender: return self._out

    def cell(self, cell_idx: int) -> BitArray:
        return self._cells[cell_idx]

    def set_cell(self, cell_idx: int, data: BitArray):
        self._cells[cell_idx] = data.trim_or_pad(self._cell_length)
        self.cell_changed.invoke(self, cell_idx)
        if self.name:
            print(f"MEMORY ({self.name}) changing cell ({cell_idx}) to {self._cells[cell_idx].to_bit_string()}")

    def reset(self):
        for cell in self._cells:
            cell.set_all(False)
        self.resetted.invoke(self, None)

    def _on_rd_signal_changed(self, sender, _):
        if not self._in_rd.signal().has_all_set(): return
        address = self._in_address.signal().to_int32()
        self._out.set_data(self._cells[address])

    def _on_wr_signal_changed(self, sender, _):
        if not self._in_wr.signal().has_all_set(): return
        address = self._in_address.signal().to_int32()
        self.set_cell(address, self._in_buffer.signal())

class SlowMemory(Memory):
    def __init__(self, length: int, cell_length: int, clock: Clock,
                 delay_rd: int, delay_wr: int,
                 address_sender: ISignalSender, in_buffer_sender: ISignalSender,
                 rd_sender: Optional[ISignalSender], wr_sender: Optional[ISignalSender],
                 name: Optional[str] = None):
        super().__init__(length, cell_length, address_sender, in_buffer_sender, rd_sender, wr_sender, name)
        
        self._clock = clock
        self._clock.stepped += self._on_clock_tick
        self._delay_rd = delay_rd
        self._delay_wr = delay_wr
        self._counter_rd = delay_rd + 1
        self._counter_wr = delay_wr + 1

    def _on_rd_signal_changed(self, sender, _):
        if not self._in_rd.signal().has_all_set():
            self._counter_rd = self._delay_rd + 1
            return
        if self._counter_rd < self._delay_rd: return
        self._counter_rd = 0

    def _on_wr_signal_changed(self, sender, _):
        if not self._in_wr.signal().has_all_set():
            self._counter_wr = self._delay_wr + 1
            return
        if self._counter_wr < self._delay_wr: return
        self._counter_wr = 0

    def _on_clock_tick(self, sender, _):
        if self._counter_rd <= self._delay_rd: self._counter_rd += 1
        if self._counter_wr <= self._delay_wr: self._counter_wr += 1

        if self._counter_rd == self._delay_rd:
            address = self._in_address.signal().to_int32()
            self._out.set_data(self.cell(address))

        if self._counter_wr == self._delay_wr:
            address = self._in_address.signal().to_int32()
            self.set_cell(address, self._in_buffer.signal())