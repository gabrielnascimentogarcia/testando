import pytest
import textwrap
from src.mic1.mic1 import Mic1
from src.mic1.assembler_v2 import AssemblerV2

class TestControlUnit:
    def test_control_unit_initial_state(self):
        mic1 = Mic1()
        assert mic1.control_unit.mpc.out_sig.signal().to_int32() == 0
        mic1.step_cycle()
        mic1.step_micro()

class TestMic1Full:
    def assemble_and_load(self, mic1, code):
        AssemblerV2.assemble(mic1.mp, textwrap.dedent(code))

    def test_multiplication_demo(self):
        mic1 = Mic1()
        code = """
        LOCO 5
        STOD x
        LOCO 4
        STOD y
        LOCO 0
        STOD res
        
        LOOP: LODD x
        JZER END
        SUBD c1
        STOD x
        LODD res
        ADDD y
        STOD res
        JUMP LOOP
        
        END: LODD res
        STOD final
        HALT: JUMP HALT
        
        x: 0
        y: 0
        res: 0
        final: 0
        c1: 1
        """
        self.assemble_and_load(mic1, code)
        
        # 3000 ciclos para garantir que SlowMemory (delay=6) tenha tempo
        for _ in range(10000):
            mic1.step_macro()
            
        assert mic1.registers[1].out_sig.signal().to_int32() == 20