from typing import Callable, List
from src.utils.bit_utils import BitArray
from src.components.signals import ISignalSender, SignalSender, SingleSignalSender

class Alu:
    def __init__(self, in_a: ISignalSender, in_b: ISignalSender, in_control: ISignalSender):
        if len(in_a.signal()) != len(in_b.signal()):
            raise ValueError("Input signals must be of the same size.")
        
        self._in_a = in_a
        self._in_b = in_b
        self._in_control = in_control
        
        self._out = SignalSender(len(self._in_a.signal()))
        self._out_n = SingleSignalSender()
        self._out_z = SingleSignalSender()

        self._functions = [self.sum_op, self.and_op, self.identity_op, self.inverse_op]

        self._in_a.signal_changed += self._update
        self._in_b.signal_changed += self._update
        self._in_control.signal_changed += self._update

    @property
    def out_sig(self) -> ISignalSender: return self._out
    @property
    def out_n(self) -> ISignalSender: return self._out_n
    @property
    def out_z(self) -> ISignalSender: return self._out_z

    def _update(self, sender, _):
        idx = self._in_control.signal().to_int32()
        if 0 <= idx < len(self._functions):
            result = self._functions[idx](self._in_a.signal(), self._in_b.signal())
        else:
            result = BitArray(len(self._in_a.signal())) # Fallback

        self._out.set_data(result)
        self._out_n.set_enable(result[len(result) - 1])
        self._out_z.set_enable(not result.has_any_set())

    @staticmethod
    def sum_op(a: BitArray, b: BitArray) -> BitArray:
        if len(a) != len(b): raise ValueError("BitArrays must be same length")
        result = BitArray(len(a))
        carry = False
        for i in range(len(a)):
            bit_a = a[i]
            bit_b = b[i]
            # Python bitwise XOR for bools
            result[i] = bit_a ^ bit_b ^ carry
            carry = (bit_a and bit_b) or (bit_a and carry) or (bit_b and carry)
        return result

    @staticmethod
    def and_op(a: BitArray, b: BitArray) -> BitArray:
        res = a.clone()
        res.and_op(b)
        return res

    @staticmethod
    def identity_op(a: BitArray, b: BitArray) -> BitArray:
        return BitArray(a)

    @staticmethod
    def inverse_op(a: BitArray, b: BitArray) -> BitArray:
        res = a.clone()
        res.not_op()
        return res