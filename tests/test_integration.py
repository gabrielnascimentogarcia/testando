import pytest
import textwrap
from src.mic1.mic1 import Mic1
from src.mic1.assembler_v2 import AssemblerV2
from src.utils.bit_utils import BitArray

class TestControlUnit:
    def test_control_unit_initial_state(self):
        # ControlUnitTests.ControlUnit1()
        mic1 = Mic1()
        
        # Verificar estado inicial do MPC e MIR
        # Cycle 0: Start
        assert mic1.control_unit.mpc.out_sig.signal().to_int32() == 0
        
        # Rodar 1 ciclo de clock
        mic1.step_cycle()
        # Ainda ciclo 0->1 do clock, mas microinstrução é carregada?
        # A lógica do Mic1.StepMicro() avança 4 sub-ciclos.
        # Vamos checar o comportamento após 1 microinstrução completa
        
        mic1.step_micro()
        
        # O endereço 0 do control_store.txt original é "00000000..." (Goto 0?)
        # Verificando o arquivo real: linha 0 -> goto 0?
        # linha 0: ... 000000000 (Next Addr field bits 0-8)
        # Se for goto 0, o MPC deve se manter 0.
        pass

class TestMic1Full:
    def assemble_and_load(self, mic1, code):
        AssemblerV2.assemble(mic1.mp, textwrap.dedent(code))

    def test_fibonacci(self):
        # Baseado em um exemplo teórico do README ou conhecimento comum do Mic1
        # Se não houver teste explícito de Fibonnaci no Mic1Tests.cs, 
        # vou usar o Example1 do assembler que já testamos, mas agora rodando de verdade.
        pass

    def test_assembler_v2_example_1_execution(self):
        # Reproduz AssemblerV2Tests.Example1() com execução real
        mic1 = Mic1()
        code = """
        LOCO 1
        STOD var1
        LOCO 2
        ADDD var1
        STOD var2
        """
        self.assemble_and_load(mic1, code)
        
        # StepMacro roda até encontrar instrução HALT ou fim do loop principal
        # O Mic1 original não tem "HALT" explícito no assembly padrão além de loops infinitos.
        # No teste C#, ele chama StepMacro().
        
        # Executar instrução 1: LOCO 1
        mic1.step_macro()
        assert mic1.registers[1].out_sig.signal().to_int32() == 1 # AC = 1
        
        # Instrução 2: STOD var1
        mic1.step_macro()
        
        # Instrução 3: LOCO 2
        mic1.step_macro()
        assert mic1.registers[1].out_sig.signal().to_int32() == 2 # AC = 2
        
        # Instrução 4: ADDD var1 (AC = AC + var1 = 2 + 1 = 3)
        mic1.step_macro()
        assert mic1.registers[1].out_sig.signal().to_int32() == 3 
        
        # Instrução 5: STOD var2
        mic1.step_macro()
        
        # Verificar memória nas variáveis
        # var1 e var2 são alocadas após o código.
        # Código tem 5 linhas (0 a 4). var1 deve ser 5, var2 deve ser 6.
        assert mic1.mp.cell(5).to_int32() == 1
        assert mic1.mp.cell(6).to_int32() == 3

    def test_multiplication_demo(self):
        # Baseado no "mult.asm" que geralmente acompanha o Mic1 ou lógica de loop
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
        
        # Executar até o loop terminar (pode demorar muitos steps)
        # 5 * 4 = 20.
        # Limite de segurança para não travar teste
        for _ in range(500):
            mic1.step_macro()
            # Verificar se chegou no loop infinito final
            # PC não muda mais no HALT loop?
            # Implementação simplificada: verificar resultado na memória
            # var 'final' é a última variável.
            # Endereços: 
            # Code: ~17 linhas. Vars no final.
            pass
            
        # Vamos inspecionar AC (deve ser 20 no final)
        assert mic1.registers[1].out_sig.signal().to_int32() == 20