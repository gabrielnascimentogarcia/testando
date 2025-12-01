from src.components.clock import Clock, ClockDelayedSignalSender
from src.components.register import Register
from src.components.multiplexer import Multiplexer
from src.components.latch import Latch
from src.components.alu import Alu
from src.components.shifter import Shifter
from src.components.memory import SlowMemory
from src.components.signals import ISignalSender, SignalSender
from src.components.processed_signals import ProcessedSignalSender, CombinationalSignalSender
from src.mic1.mi_register import MIRegister
from src.mic1.control_unit import ControlUnit
from src.utils.bit_utils import BitArray
from typing import List

class Mic1:
    def __init__(self):
        self.clock = Clock(4)
        self.mir = MIRegister()
        self.mir.set_control_sender(self.clock.signal(0))
        self.resetted = None # Placeholder for event if needed

        self.registers = [
            Register(16, name="PC"), Register(16, name="AC"), Register(16, name="SP"), Register(16, name="IR"),
            Register(16, name="TIR"), Register(16, name="ZERO"), Register(16, name="PLUS1"), Register(16, name="MINUS1"),
            Register(16, name="AMASk"), Register(16, name="SMASK"), Register(16, name="A"), Register(16, name="B"),
            Register(16, name="C"), Register(16, name="D"), Register(16, name="E"), Register(16, name="F"),
        ]

        # Init Constants
        self.registers[2].set_data(BitArray.from_bit_string("0001000000000000"))
        self.registers[6].set_data(BitArray.from_bit_string("0000000000000001"))
        self.registers[7].set_data(BitArray.from_bit_string("1111111111111111"))
        self.registers[8].set_data(BitArray.from_bit_string("0000111111111111"))
        self.registers[9].set_data(BitArray.from_bit_string("0000000011111111"))

        regs_out = [r.out_sig for r in self.registers]
        self._a = Multiplexer(16, regs_out, self.mir.out_a)
        self._b = Multiplexer(16, regs_out, self.mir.out_b)
        self._c = ProcessedSignalSender.decoder4to16(self.mir.out_c)

        self.latch_a = Latch(self._a.out_sig, self.clock.signal(1))
        self.latch_b = Latch(self._b.out_sig, self.clock.signal(1))

        self.mbr_rd = Register(16, name="MBR_RD")
        self._a_mux = Multiplexer(16, [self.latch_a.out_sig, self.mbr_rd.out_sig], self.mir.out_a_mux)

        self.alu = Alu(self._a_mux.out_sig, self.latch_b.out_sig, self.mir.out_alu)
        self.shifter = Shifter(self.alu.out_sig, self.mir.out_shifter)

        for i in range(len(self.registers)):
            self.registers[i].set_data_sender(self.shifter.out_sig)
            
            # Combinational AND logic: C[i] AND ENC AND Clock(3)
            c_i = ProcessedSignalSender.interval(self._c, i, 1)
            ctrl_sig = CombinationalSignalSender.and_op([
                c_i,
                self.mir.out_enc,
                self.clock.signal(3)
            ])
            self.registers[i].set_control_sender(ctrl_sig)

        mbr_wr_ctrl = CombinationalSignalSender.and_op([self.mir.out_mbr, self.mir.out_wr, self.clock.signal(3)])
        self.mbr_wr = Register(16, data_sender=self.shifter.out_sig, control_sender=mbr_wr_ctrl, name="MBR_WR")
        
        self.mar = Register(16, data_sender=self.latch_b.out_sig, control_sender=self.clock.signal(2), name="MAR")

        # Memory Address Logic: trim 16 bit MAR to 12 bit address for 4096 words
        mem_addr = ProcessedSignalSender(self.mar.out_sig, lambda data: data.trim_or_pad(12))

        self.mp = SlowMemory(4096, 16, self.clock, 6, 6,
            mem_addr, self.mbr_wr.out_sig,
            self.mir.out_rd, self.mir.out_wr, name="MP"
        )

        self.mbr_rd.set_data_sender(self.mp.out_sig)
        
        # MBR RD Control: Delayed RD AND Clock(3)
        delayed_rd = ClockDelayedSignalSender(self.mir.out_rd, self.clock, 0)
        mbr_rd_ctrl = CombinationalSignalSender.and_op([delayed_rd, self.clock.signal(3)])
        self.mbr_rd.set_control_sender(mbr_rd_ctrl)

        self.control_unit = ControlUnit(self.alu.out_n, self.alu.out_z, self.clock, self.mir)

    def reset(self):
        for r in self.registers: r.reset()
        # Restore constants
        self.registers[2].set_data(BitArray.from_bit_string("0001000000000000"))
        self.registers[6].set_data(BitArray.from_bit_string("0000000000000001"))
        self.registers[7].set_data(BitArray.from_bit_string("1111111111111111"))
        self.registers[8].set_data(BitArray.from_bit_string("0000111111111111"))
        self.registers[9].set_data(BitArray.from_bit_string("0000000011111111"))

        self.control_unit.reset()
        self.latch_a.reset()
        self.latch_b.reset()
        self.mp.reset()
        self.mbr_rd.reset()
        self.mbr_wr.reset()
        self.mar.reset()

    def step_cycle(self):
        self.clock.step()

    def step_micro(self):
        if self.clock.current_cycle() < 0: self.step_cycle()
        self.step_cycle()
        while self.clock.current_cycle() > 0:
            self.clock.step()

    def step_macro(self):
        self.step_micro()
        while self.control_unit.mpc.out_sig.signal().has_any_set():
            self.step_micro()