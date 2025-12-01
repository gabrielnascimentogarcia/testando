import re
from src.components.memory import Memory
from src.utils.bit_utils import BitArray

class Assembler:
    INSTRUCTION_SET = {
        "LODD": "0000", "STOD": "0001", "ADDD": "0010", "SUBD": "0011",
        "JPOS": "0100", "JZER": "0101", "JUMP": "0110", "LOCO": "0111",
        "LODL": "1000", "STOL": "1001", "ADDL": "1010", "SUBL": "1011",
        "JNEG": "1100", "JNZE": "1101", "CALL": "1110",
        "PSHI": "1111000", "POPI": "1111001", "PUSH": "1111010", "POP": "1111011",
        "RETN": "1111100", "SWAP": "1111101", "INSP": "1111110", "DESP": "1111111"
    }

    # C#: ^(?:([A-Za-z]+):\s+)?([A-Za-z]+)(?:\s+([A-Za-z_][A-Za-z0-9_]*|\d+))?$
    _LINE_REGEX = re.compile(
        r"^(?:([A-Za-z]+):\s+)?([A-Za-z]+)(?:\s+([A-Za-z_][A-Za-z0-9_]*|\d+))?$"
    )

    @staticmethod
    def assemble(mp: Memory, assembly_code: str):
        lines = [line for line in re.split(r'[\n\r]', assembly_code) if line.strip()]

        instructions = []
        addresses = {}
        variables = set()
        current_address = 0

        for line in lines:
            valid, result = Assembler.process_line(line)
            if not valid:
                raise Exception("instruction not valid")
            
            op_code, op, label = result
            instructions.append(result)

            if label is not None:
                addresses[label] = current_address
                if label in variables:
                    variables.remove(label)
            
            if op is not None and op[0].isalpha():
                if op not in addresses:
                    variables.add(op)
            
            current_address += 1

        code_size = len(instructions)
        var_offset = 0
        for variable in variables:
            if variable in addresses:
                continue
            addresses[variable] = code_size + var_offset
            var_offset += 1
        
        current_address = 0
        for op_code, op, label in instructions:
            bit_string = op_code
            
            if op is not None:
                if op[0].isalpha(): # variable or label
                    addr = addresses.get(op, 0) # Should be handled if missing? C# uses TryGetValue default
                    bit_string += BitArray.from_int(addr, 16 - len(op_code)).to_bit_string()
                else: # literal
                    bit_string += BitArray.from_int(int(op), 16 - len(op_code)).to_bit_string()
            else:
                bit_string += "0" * (16 - len(op_code))
            
            mp.set_cell(current_address, BitArray.from_bit_string(bit_string))
            current_address += 1

    @staticmethod
    def process_line(line: str):
        match = Assembler._LINE_REGEX.match(line)
        if not match:
            return False, (None, None, None)
        
        # In Python regex groups are 1-indexed based on parenthesis
        # Group 1: Label (Optional)
        # Group 2: OpLabel
        # Group 3: Op (Optional)
        
        label = match.group(1)
        op_label = match.group(2)
        op = match.group(3)

        # Case insensitive lookup
        # Simulate C# StringComparer.OrdinalIgnoreCase by upper-casing key if needed or searching manually
        # Since keys in INSTRUCTION_SET are caps, let's upper the op_label
        op_code = Assembler.INSTRUCTION_SET.get(op_label.upper())
        if op_code is None:
            return False, (None, None, None)

        return True, (op_code, op, label)