import pytest
from src.utils.bit_utils import BitArray
from src.mic1.mic1 import Mic1

def test_bitarray_ops():
    b1 = BitArray.from_bit_string("1010")
    b2 = BitArray.from_bit_string("1100")
    
    # Test And
    b3 = b1.clone().and_op(b2)
    assert b3.to_bit_string() == "1000"
    
    # Test Shift Left (1010 -> 0100 in C# logic provided? No, 
    # C# code says: shifted[i] = input[i+1]. Index 0 gets Index 1. 
    # Index 0 is LSB. So LSB gets bit 1. This is a RIGHT shift arithmetically.
    # "1010" (MSB..LSB) is indices 3,2,1,0 -> 1,0,1,0.
    # shifted[0] = input[1] (1). shifted[1] = input[2] (0). shifted[2] = input[3] (1).
    # Result bits: 1,0,1,0 (padded at end?). shifted[3] (MSB) undefined in loop? 
    # C# Loop: i < length-1. shifted[length-1] stays default (False).
    # Result bits: 1, 0, 1, 0(False). -> 0101 (MSB..LSB).
    # Wait, lets re-verify C# logic:
    # input "1010" (val 10). i=0(LSB) <- i=1.
    # shifted[0] = input[1] (which is '1' from "1010"? No.
    # "1010": bit 0 is 0. bit 1 is 1. bit 2 is 0. bit 3 is 1.
    # shifted[0] = 1. shifted[1] = 0. shifted[2] = 1. shifted[3] = 0.
    # Result bits: 1, 0, 1, 0. -> "0101" (val 5). 
    # So C# "ShiftLeft" implementation actually divides by 2 (Right Shift).
    # Let's verify python implementation matches this "weird" naming or logic.
    shifted = b1.shift_left() 
    # b1 is 1010 (val 10). Expect 0101 (val 5).
    assert shifted.to_bit_string() == "0101"

def test_mic1_instantiation():
    machine = Mic1()
    # Check Constant Registers
    # Reg 7 should be -1 (all 1s)
    assert machine.registers[7].out_sig.signal().to_bit_string() == "1111111111111111"
    # Reg 6 should be +1
    assert machine.registers[6].out_sig.signal().to_int32() == 1

def test_alu_sum():
    # Setup simple sum manually using the components logic directly
    from src.components.alu import Alu
    
    a = BitArray.from_int(5, 16)
    b = BitArray.from_int(3, 16)
    res = Alu.sum_op(a, b)
    assert res.to_int32() == 8

if __name__ == "__main__":
    pytest.main()