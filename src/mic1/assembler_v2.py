import re
from src.components.memory import Memory
from src.utils.bit_utils import BitArray
from src.mic1.exceptions.assembler_exceptions import (
    OpCodeNotDefinedException, DuplicatedSymbolException, 
    SymbolNotDefinedException, SyntaxErrorException
)

class AssemblerV2:
    INSTRUCTION_SET = {
        "LODD": "0000", "STOD": "0001", "ADDD": "0010", "SUBD": "0011",
        "JPOS": "0100", "JZER": "0101", "JUMP": "0110", "LOCO": "0111",
        "LODL": "1000", "STOL": "1001", "ADDL": "1010", "SUBL": "1011",
        "JNEG": "1100", "JNZE": "1101", "CALL": "1110",
        "PSHI": "1111000", "POPI": "1111001", "PUSH": "1111010", "POP": "1111011",
        "RETN": "1111100", "SWAP": "1111101", "INSP": "1111110", "DESP": "1111111"
    }

    IDENTIFIER = r"[a-zA-Z][a-zA-Z0-9]*"
    LITERAL = r"\d+"
    COMMENT = r"(\s*/.*)?"

    # Regex adaptados do C#
    REGEX_INSTRUCTION = re.compile(
        rf"^(?:(?P<label>{IDENTIFIER})\s*:\s*)?(?P<mnemonic>[a-zA-Z]+)(?:\s+(?P<operand>{LITERAL}|{IDENTIFIER}))?{COMMENT}$"
    )
    REGEX_SYMBOL = re.compile(
        rf"^(?P<symbol>{IDENTIFIER})\s*=\s*(?P<value>{LITERAL}){COMMENT}$"
    )
    REGEX_CONSTANT = re.compile(
        rf"^(?P<constant>{IDENTIFIER}):\s*(?P<value>{LITERAL}){COMMENT}$"
    )
    REGEX_LABEL_ONLY = re.compile(
        rf"^(?P<label>{IDENTIFIER}):{COMMENT}$"
    )
    REGEX_BLANK_OR_COMMENT = re.compile(
        rf"^{COMMENT}$"
    )

    @staticmethod
    def assemble(mp: Memory, assembly_code: str):
        symbols = {}
        labels = set()
        variables = {} 

        lines = assembly_code.replace("\r", "").split('\n')
        
        instructions = [] # List of (lineNumber, op_code, operand)

        for index, line in enumerate(lines):
            line_number = index + 1
            
            # Attempt Match Instruction
            match_instr = AssemblerV2.REGEX_INSTRUCTION.match(line)
            if match_instr:
                op_label = match_instr.group("mnemonic")
                
                # Case insensitive check for OpCode
                op_code = AssemblerV2.INSTRUCTION_SET.get(op_label.upper())
                
                if op_code is None:
                    # Se parece instrução mas o OpCode não existe
                    raise OpCodeNotDefinedException(line_number, op_label)
                
                label = match_instr.group("label")
                if label:
                    labels.add(label)
                    if label in variables: variables.pop(label)
                    
                    if label in symbols:
                        raise DuplicatedSymbolException(line_number, label)
                    symbols[label] = len(instructions)
                
                operand = match_instr.group("operand")
                is_literal = False
                if operand:
                    is_literal = re.match(f"^{AssemblerV2.LITERAL}$", operand) is not None
                
                if operand and not is_literal and operand not in symbols:
                    if operand not in variables:
                        variables[operand] = 0 # default value
                
                instructions.append((line_number, op_code, operand))
                continue

            # Attempt Match Symbol "A = 3"
            match_sym = AssemblerV2.REGEX_SYMBOL.match(line)
            if match_sym:
                identifier = match_sym.group("symbol")
                value = int(match_sym.group("value"))
                variables[identifier] = value
                
                if identifier in symbols:
                    raise DuplicatedSymbolException(line_number, identifier)
                
                symbols[identifier] = -1 # Placeholder
                continue

            # Attempt Match Constant "C: 2"
            match_const = AssemblerV2.REGEX_CONSTANT.match(line)
            if match_const:
                identifier = match_const.group("constant")
                value = int(match_const.group("value"))
                
                if identifier in symbols:
                    raise DuplicatedSymbolException(line_number, identifier)
                symbols[identifier] = value
                
                if identifier in variables:
                    variables.pop(identifier)
                continue

            # Attempt Match Label Only "LABEL:"
            match_lbl = AssemblerV2.REGEX_LABEL_ONLY.match(line)
            if match_lbl:
                identifier = match_lbl.group("label")
                labels.add(identifier)
                if identifier in variables: variables.pop(identifier)
                
                if identifier in symbols:
                    raise DuplicatedSymbolException(line_number, identifier)
                symbols[identifier] = len(instructions)
                
                if identifier in variables: variables.pop(identifier)
                continue

            # Attempt Match Blank/Comment
            match_blank = AssemblerV2.REGEX_BLANK_OR_COMMENT.match(line)
            if match_blank:
                continue

            # If nothing matched
            raise SyntaxErrorException(line_number, line)

        # Second Pass: Resolving addresses
        program_size = len(instructions)
        var_offset = 0
        
        for identifier in variables:
            symbols[identifier] = program_size + var_offset
            var_offset += 1
        
        current_address = 0
        for line_number, op_code, operand in instructions:
            value = 0
            if operand is not None:
                if re.match(f"^{AssemblerV2.LITERAL}$", operand):
                    value = int(operand)
                else:
                    if operand not in symbols:
                        raise SymbolNotDefinedException(line_number, operand)
                    value = symbols[operand]
            
            operand_bits = BitArray.from_int(value, 16 - len(op_code)).to_bit_string()
            full_bit_string = op_code + operand_bits
            
            mp.set_cell(current_address, BitArray.from_bit_string(full_bit_string))
            current_address += 1

        # Write variables at the end
        for identifier, value in variables.items():
            mp.set_cell(symbols[identifier], BitArray.from_int(value, 16))