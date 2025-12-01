import pytest
import textwrap
from src.components.memory import Memory
from src.components.signals import SignalSender
from src.mic1.assembler_v2 import AssemblerV2
from src.mic1.mic1 import Mic1
from src.utils.bit_utils import BitArray

def create_memory():
    return Memory(4096, 16, SignalSender(0), SignalSender(0), None, None, "MP")

def assemble_code(mp, code):
    # Remove indentação comum para satisfazer a regex estrita do Assembler
    AssemblerV2.assemble(mp, textwrap.dedent(code))

def test_assembler1():
    memory = create_memory()
    assembly_code = """
    LOCO 1
    STOD 4
    """
    assemble_code(memory, assembly_code)
    
    # LOCO 1 -> 0111 (LOCO) + 000000000001 (1) -> 0111000000000001
    assert BitArray.from_bit_string("0111000000000001").compare(memory.cell(0))
    # STOD 4 -> 0001 (STOD) + 000000000100 (4) -> 0001000000000100
    assert BitArray.from_bit_string("0001000000000100").compare(memory.cell(1))

def test_assembler2():
    memory = create_memory()
    assembly_code = """
    LOCO 1
    STOD var1
    STOD var1
    STOD var2
    STOD var2
    """
    assemble_code(memory, assembly_code)
    
    # 0: LOCO 1
    assert BitArray.from_bit_string("0111000000000001").compare(memory.cell(0))
    # 1: STOD var1 (var1 address should be 5 -> 0101)
    # 2: STOD var1
    assert memory.cell(1).compare(memory.cell(2))
    # 3: STOD var2 (var2 address should be 6 -> 0110)
    # 4: STOD var2
    assert memory.cell(3).compare(memory.cell(4))

def test_assembler3():
    memory = create_memory()
    assembly_code = """
    var1 = 0
    var2 = 0
    LOCO 1
    STOD var1
    STOD var1
    STOD var2
    STOD var2
    """
    assemble_code(memory, assembly_code)
    
    # Same logic as assembler2
    assert BitArray.from_bit_string("0111000000000001").compare(memory.cell(0))
    assert memory.cell(1).compare(memory.cell(2))
    assert memory.cell(3).compare(memory.cell(4))

def test_example1_run():
    # Integração: Montar e Executar (Parcial sem Control Store)
    mic1 = Mic1()
    assembly_code = """
    LOCO 1
    STOD var1
    LOCO 2
    ADDD var1
    STOD var2
    """
    assemble_code(mic1.mp, assembly_code)
    # Sem control_store.txt, não podemos chamar step_macro ainda
    # mic1.step_macro()

def test_constant():
    mic1 = Mic1()
    assembly_code = """
    C0: 0
    C1: 1
    C10: 10
    LOCO C0
    LOCO C1
    LOCO C10
    """
    assemble_code(mic1.mp, assembly_code)
    
    # LOCO C0 -> LOCO 0
    assert mic1.mp.cell(0).compare(BitArray.from_bit_string("0111000000000000"))
    # LOCO C1 -> LOCO 1
    assert mic1.mp.cell(1).compare(BitArray.from_bit_string("0111000000000001"))
    # LOCO C10 -> LOCO 10 (1010 binary)
    assert mic1.mp.cell(2).compare(BitArray.from_bit_string("0111000000001010"))

if __name__ == "__main__":
    pytest.main()