from typing import List, Callable, Optional
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, EventHandler

class ProcessedSignalSender(ISignalSender):
    def __init__(self, source: ISignalSender, func: Callable[[BitArray], BitArray]):
        self._source = source
        self._func = func
        self._signal_changed = EventHandler()
        # O setter agora permite que esta linha funcione
        self._source.signal_changed += self._on_signal_change

    @property
    def signal_changed(self):
        return self._signal_changed

    @signal_changed.setter
    def signal_changed(self, value):
        self._signal_changed = value

    @property
    def length(self):
        return self.signal().length

    def signal(self) -> BitArray:
        return self._func(self._source.signal())

    def _on_signal_change(self, sender, _):
        self._signal_changed.invoke(sender, self._func(self._source.signal()))

    @staticmethod
    def interval(source: ISignalSender, offset: int, length: int) -> ISignalSender:
        def func(signal: BitArray) -> BitArray:
            result = BitArray(length)
            for i in range(length):
                if (i + offset) < len(signal):
                    result[i] = signal[i + offset]
            return result
        return ProcessedSignalSender(source, func)

    @staticmethod
    def increment(source: ISignalSender, increment_val: int = 1) -> ISignalSender:
        def func(signal: BitArray) -> BitArray:
            value = signal.to_int32() + increment_val
            inc_bits = BitArray.from_int(value, 32)
            result = BitArray(len(signal))
            for i in range(len(signal)):
                if i < len(inc_bits):
                    result[i] = inc_bits[i]
            return result
        return ProcessedSignalSender(source, func)

    @staticmethod
    def decoder4to16(source: ISignalSender) -> ISignalSender:
        def func(input_sig: BitArray) -> BitArray:
            value = 0
            for i in range(4):
                if i < len(input_sig) and input_sig[i]:
                    value |= (1 << i)
            
            result = BitArray(16, False)
            if 0 <= value < 16:
                result[value] = True
            return result
        return ProcessedSignalSender(source, func)

class CombinationalSignalSender(ISignalSender):
    def __init__(self, sources: List[ISignalSender], func: Callable[[List[BitArray]], BitArray]):
        self._sources = sources
        self._func = func
        self._signal_changed = EventHandler()
        for src in self._sources:
            src.signal_changed += self._on_signal_change
    
    @property
    def signal_changed(self):
        return self._signal_changed
    
    @signal_changed.setter
    def signal_changed(self, value):
        self._signal_changed = value

    @property
    def length(self):
        return self.signal().length

    def signal(self) -> BitArray:
        signals = [s.signal() for s in self._sources]
        return self._func(signals)

    def _on_signal_change(self, sender, _):
        signals = [s.signal() for s in self._sources]
        self._signal_changed.invoke(self, self._func(signals))

    @staticmethod
    def and_op(sources: List[ISignalSender]) -> 'CombinationalSignalSender':
        def func(signals: List[BitArray]) -> BitArray:
            if not signals:
                return BitArray(0)
            
            min_length = min(s.length for s in signals)
            result = signals[0].clone()
            result = result.trim_or_pad(min_length)

            for i in range(1, len(signals)):
                other = signals[i].clone().trim_or_pad(min_length)
                result.and_op(other)
            return result
        
        return CombinationalSignalSender(sources, func)