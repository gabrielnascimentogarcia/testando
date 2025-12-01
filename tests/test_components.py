import pytest
from src.components.register import Register
from src.components.memory import Memory
from src.components.signals import SignalSender, SingleSignalSender
from src.utils.bit_utils import BitArray

class TestRegister:
    def test_register_1(self):
        # RegisterTests.Register1()
        register = Register(16)
        in_sender = SignalSender(16)
        control_sender = SingleSignalSender()
        
        register.set_data_sender(in_sender)
        register.set_control_sender(control_sender)
        
        # Act 1: Data change, control disable
        in_sender.set_data(BitArray.from_bit_string("1010101010101010"))
        control_sender.disable()
        # Assert 1: Out should be 0 (default)
        assert register.out_sig.signal().to_bit_string() == "0000000000000000"
        
        # Act 2: Enable control
        control_sender.enable()
        # Assert 2: Out should update
        assert register.out_sig.signal().to_bit_string() == "1010101010101010"
        
        # Act 3: Data change while enabled
        in_sender.set_data(BitArray.from_bit_string("1111111111111111"))
        # Assert 3
        assert register.out_sig.signal().to_bit_string() == "1111111111111111"

class TestMemory:
    def test_memory_1(self):
        # MemoryTests.Memory1()
        addr_sender = SignalSender(16)
        in_sender = SignalSender(16)
        rd_sender = SingleSignalSender()
        wr_sender = SingleSignalSender()
        
        mem = Memory(4096, 16, addr_sender, in_sender, rd_sender, wr_sender, "MP")
        
        # Write
        addr_sender.set_data(BitArray.from_int(10, 16))
        in_sender.set_data(BitArray.from_int(21, 16))
        wr_sender.pulse()
        
        # Read
        wr_sender.disable()
        rd_sender.enable()
        
        # Verify cell content directly and output
        assert mem.cell(10).to_int32() == 21
        assert mem.out_sig.signal().to_int32() == 21