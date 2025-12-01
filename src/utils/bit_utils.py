from typing import List, Union

class BitArray:
    """
    Simula o comportamento do System.Collections.BitArray do C#
    Index 0 é o bit menos significativo (LSB) se criado via from_int.
    """
    def __init__(self, length_or_bits: Union[int, List[bool], 'BitArray'], default: bool = False):
        if isinstance(length_or_bits, int):
            self.length = length_or_bits
            self.bits = [default] * self.length
        elif isinstance(length_or_bits, list):
            self.bits = list(length_or_bits) # Copy
            self.length = len(self.bits)
        elif isinstance(length_or_bits, BitArray):
            self.bits = list(length_or_bits.bits)
            self.length = length_or_bits.length
        else:
            raise ValueError("Invalid initializer for BitArray")

    def __getitem__(self, index: int) -> bool:
        if index < 0 or index >= self.length:
             raise IndexError("BitArray index out of range")
        return self.bits[index]

    def __setitem__(self, index: int, value: bool):
        if index < 0 or index >= self.length:
             raise IndexError("BitArray index out of range")
        self.bits[index] = value

    def __len__(self) -> int:
        return self.length

    def set_all(self, value: bool):
        for i in range(self.length):
            self.bits[i] = value

    def clone(self) -> 'BitArray':
        return BitArray(self)

    def copy_to(self, array: List[int], index: int):
        # Implementação simplificada para ToInt32
        val = self.to_int32()
        array[index] = val

    def and_op(self, other: 'BitArray') -> 'BitArray':
        length = min(self.length, other.length)
        for i in range(length):
            self.bits[i] = self.bits[i] and other.bits[i]
        return self

    def not_op(self) -> 'BitArray':
        for i in range(self.length):
            self.bits[i] = not self.bits[i]
        return self

    def has_all_set(self) -> bool:
        return all(self.bits)

    def has_any_set(self) -> bool:
        return any(self.bits)
    
    def get(self, index: int) -> bool:
        return self[index]

    def to_int32(self) -> int:
        if self.length > 32:
            raise ValueError("BitArray length must be at most 32 bits.")
        value = 0
        for i in range(self.length):
            if self.bits[i]:
                value |= (1 << i)
        return value

    def to_bit_string(self) -> str:
        # C# ToBitString: chars[bits.Length - 1 - i] = bits[i]
        # Mostra MSB à esquerda
        chars = ['1' if self.bits[i] else '0' for i in range(self.length)]
        return "".join(reversed(chars))

    @staticmethod
    def from_int(value: int, length: int) -> 'BitArray':
        bits = BitArray(length)
        for i in range(length):
            bits[i] = (value & (1 << i)) != 0
        return bits

    @staticmethod
    def from_bit_string(bit_string: str, lmsb: bool = True) -> 'BitArray':
        length = len(bit_string)
        bits = BitArray(length)
        for i in range(length):
            c = bit_string[length - 1 - i] if lmsb else bit_string[i]
            if c == '1':
                bits[i] = True
            elif c == '0':
                bits[i] = False
            else:
                raise ValueError("bitString must contain only '0's and '1's.")
        return bits

    def trim_or_pad(self, target_length: int) -> 'BitArray':
        result = BitArray(target_length)
        l = min(self.length, target_length)
        for i in range(l):
            result[i] = self.bits[i]
        return result

    def shift_left(self) -> 'BitArray':
        # C#: shifted[i] = input[i+1] (shift lógico para direita na representação array, 
        # mas "Left" no valor numérico visual MSB..LSB? 
        # Vamos seguir a lógica exata do C# code fornecido:
        # shifted[i] = input[i + 1];
        # Isso significa que o bit 0 recebe o bit 1. O bit N-1 fica false.
        # Isso é um shift right aritmético se index 0 for LSB.
        # Mas o nome é ShiftLeft. Vamos confiar no código C#.
        shifted = BitArray(self.length)
        for i in range(self.length - 1):
            shifted[i] = self.bits[i+1]
        return shifted

    def shift_right(self) -> 'BitArray':
        # C#: shifted[i] = input[i - 1]; 
        shifted = BitArray(self.length)
        for i in range(1, self.length):
            shifted[i] = self.bits[i-1]
        return shifted

    def compare(self, other: 'BitArray') -> bool:
        if self.length != other.length: return False
        return self.bits == other.bits