import pytest
from src.components.register import Register
from src.components.memory import Memory
from src.components.signals import SignalSender, SingleSignalSender
from src.utils.bit_utils import BitArray

class TestRegister:
    def test_register_1(self):
        register = Register(16)
        in_sender = SignalSender(16)
        control_sender = SingleSignalSender()
        
        register.set_data_sender(in_sender)
        register.set_control_sender(control_sender)
        
        # Test 1: Control Disabled -> No Update
        in_sender.set_data(BitArray.from_bit_string("1010101010101010"))
        control_sender.disable()
        assert register.out_sig.signal().to_bit_string() == "0000000000000000"
        
        # Test 2: Enable Control -> Update Happens
        control_sender.enable()
        assert register.out_sig.signal().to_bit_string() == "1010101010101010"
        
        # Test 3: Data Change while Enabled -> Requires Toggle in this implementation logic
        in_sender.set_data(BitArray.from_bit_string("1111111111111111"))
        control_sender.disable()
        control_sender.enable()
        assert register.out_sig.signal().to_bit_string() == "1111111111111111"

class TestMemory:
    def test_memory_1(self):
        addr_sender = SignalSender(16)
        in_sender = SignalSender(16)
        rd_sender = SingleSignalSender()
        wr_sender = SingleSignalSender()
        mem = Memory(4096, 16, addr_sender, in_sender, rd_sender, wr_sender, "MP")
        
        addr_sender.set_data(BitArray.from_int(10, 16))
        in_sender.set_data(BitArray.from_int(21, 16))
        wr_sender.pulse()
        
        wr_sender.disable()
        rd_sender.enable()
        
        assert mem.cell(10).to_int32() == 21
        assert mem.out_sig.signal().to_int32() == 21