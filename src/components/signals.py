from abc import ABC, abstractmethod
from typing import List, Callable
from src.utils.bit_utils import BitArray

class EventHandler:
    """Simples implementação de C# events"""
    def __init__(self):
        self._listeners = []
    
    def __iadd__(self, listener):
        self._listeners.append(listener)
        return self
    
    def __isub__(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)
        return self
    
    def invoke(self, sender, args):
        for listener in self._listeners:
            listener(sender, args)

class ISignalSender(ABC):
    @abstractmethod
    def signal(self) -> BitArray:
        pass
    
    @property
    @abstractmethod
    def signal_changed(self) -> EventHandler:
        pass

class SignalSender(ISignalSender):
    def __init__(self, data_or_length):
        self._signal_changed = EventHandler()
        if isinstance(data_or_length, int):
            self._data = BitArray(data_or_length)
        elif isinstance(data_or_length, BitArray):
            self._data = data_or_length
        else:
            raise ValueError("Invalid argument for SignalSender")

    @property
    def signal_changed(self):
        return self._signal_changed
    
    @signal_changed.setter
    def signal_changed(self, value):
        self._signal_changed = value

    def set_data(self, data: BitArray):
        self._data = data.trim_or_pad(self._data.length)
        self._signal_changed.invoke(self, self._data)

    def signal(self) -> BitArray:
        return BitArray(self._data)

class SingleSignalSender(SignalSender):
    def __init__(self, bit: bool = False):
        super().__init__(BitArray([bit]))

    def enable(self):
        if self.signal().has_all_set(): return
        self.set_data(BitArray([True]))

    def disable(self):
        if not self.signal().has_all_set(): return
        self.set_data(BitArray([False]))

    def set_enable(self, enable: bool):
        if enable: self.enable()
        else: self.disable()

    def pulse(self):
        self.enable()
        self.disable()