from typing import List
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SingleSignalSender, EventHandler

class Clock:
    def __init__(self, cycles: int):
        self._cycles = cycles
        self._current_cycle = -1
        self._signals = [SingleSignalSender() for _ in range(cycles)]
        self.stepped = EventHandler()

    def current_cycle(self) -> int:
        return self._current_cycle
    
    def signal(self, cycle: int) -> ISignalSender:
        return self._signals[cycle]
    
    def reset(self):
        if self._current_cycle >= 0:
            self._signals[self._current_cycle].disable()
        self._current_cycle = -1

    def step(self):
        if self._current_cycle >= 0:
            self._signals[self._current_cycle].disable()
            self.stepped.invoke(self, None)
        
        self._current_cycle += 1
        if self._current_cycle >= self._cycles:
            self._current_cycle = 0
        
        self._signals[self._current_cycle].enable()

class ClockDelayedSignalSender(ISignalSender):
    def __init__(self, source: ISignalSender, clock: Clock, delay: int):
        self._source = source
        self._clock = clock
        self._delay = delay
        self._counter = 0
        self._buffer = BitArray(len(source.signal()))
        
        self._signal_changed = EventHandler()
        
        self._source.signal_changed += self._on_signal_changed
        self._clock.stepped += self._on_step

    @property
    def signal_changed(self):
        return self._signal_changed

    @signal_changed.setter
    def signal_changed(self, value):
        self._signal_changed = value

    def signal(self) -> BitArray:
        return BitArray(self._buffer)

    def _on_signal_changed(self, sender, _):
        if self._counter < self._delay: return
        self._counter = 0
        if self._delay == 0:
            self._buffer = self._source.signal()
            self._signal_changed.invoke(self, self._buffer)

    def _on_step(self, sender, _):
        if self._counter <= self._delay:
            self._counter += 1
        
        if self._counter == self._delay:
            self._buffer = self._source.signal()
            self._signal_changed.invoke(self, self._buffer)