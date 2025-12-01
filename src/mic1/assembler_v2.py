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

    # Adaptando Regex C# para Python (?<name>) -> (?P<name>)
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
        variables = {} # Dict<string, int>

        lines = assembly_code.replace("\r", "").split('\n')
        
        # List of (lineNumber, op_code, operand)
        instructions = []

        for index, line in enumerate(lines):
            line_number = index + 1
            
            # 1. Check Instruction
            match = AssemblerV2.REGEX_INSTRUCTION.match(line)
            # Need to verify if it's not actually a Symbol/Constant/LabelOnly mistaken for instruction
            # The regexes in C# are quite specific. Let's strictly follow the order or specificity.
            # In C#, RegexInstruction covers cases with optional operands.
            # However, "LABEL:" matches Instruction regex as mnemonic="LABEL" if we aren't careful?
            # No, mnemonic is [a-zA-Z]+. "LABEL:" has a colon. 
            # The C# regex `^((?<label>...)\s*:\s*)?(?<mnemonic>...)...` handles the label part.
            # Let's check matches in order of the original code.

            # Note: C# code checks regexes in a specific order but `RegexInstruction` is checked FIRST.
            # If `RegexInstruction` matches, it processes it.
            
            if match:
                # But wait, does RegexInstruction match "A = 3"? 
                # Mnemonic would be "A", operand "=", which is not Identifier or Literal. So no.
                # Does it match "C: 2"?
                # Label "C", mnemonic "2"? No mnemonic is alpha.
                # Does it match "LABEL:"?
                # Label "LABEL", mnemonic? Required by regex `(?<mnemonic>[a-zA-Z]+)`. 
                # So "LABEL:" line alone won't match Instruction if there is no mnemonic after colon.
                
                op_label = match.group("mnemonic")
                
                # Check if it is a valid op_code first? The C# code checks Dictionary immediately.
                # If not in dictionary, it throws OpCodeNotDefinedException.
                # BUT, could it be one of the other regex forms?
                # The C# code structure is: if (match.Success) { try get opcode; if fail throw; ... continue; }
                # So if RegexInstruction matches structure, it assumes it IS an instruction.
                
                # We need to be careful: "LABEL:" might match if the regex allows empty mnemonic? No, `+`.
                pass

            # Let's reproduce the exact flow.
            
            # Attempt Match Instruction
            match_instr = AssemblerV2.REGEX_INSTRUCTION.match(line)
            if match_instr:
                op_label = match_instr.group("mnemonic")
                
                # Case insensitive check for OpCode
                # Since dict keys are UPPER, we iterate or check upper
                op_code = AssemblerV2.INSTRUCTION_SET.get(op_label.upper())
                
                if op_code is None:
                    # If it matches the instruction structure but isn't an opcode, 
                    # we must check if it might be another pattern (like LabelOnly or Symbol)
                    # BEFORE throwing?
                    # The C# code says: if (match.Success) { ... if (!TryGetValue) throw ... }
                    # This implies "Label: Mnemonic Operand" is exclusively an instruction structure.
                    # "Label:" alone does NOT match `(?<mnemonic>[a-zA-Z]+)`?
                    # Wait, if `RegexInstruction` is strict, it requires mnemonic.
                    
                    # Problem: "VAR = 10". 
                    # label=None, mnemonic="VAR", operand=None? No, "=" remains. regex expects space then operand.
                    # So "VAR = 10" does not match Instruction regex.
                    
                    # Problem: "LABEL:"
                    # label="LABEL", mnemonic=""? No, mnemonic is `+`. Matches nothing.
                    
                    # So if it matches Instruction Regex, it IS intended to be an instruction.
                    raise OpCodeNotDefinedException(line_number, op_label)
                
                label = match_instr.group("label")
                if label:
                    labels.add(label)
                    if label in variables: variables.pop(label)
                    
                    if label in symbols:
                        raise DuplicatedSymbolException(line_number, label)
                    symbols[label] = len(instructions)
                
                operand = match_instr.group("operand")
                # Check if operand is literal
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
                    # In C# it attempts TryAdd(..., -1). If fail, Throw.
                    # This means you cannot redefine a symbol even if it was just a forward ref? 
                    # The C# code logic: `if (!symbols.TryAdd(identifier, -1))` -> throw.
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
        
        # Assign addresses to variables (that are in `variables` dict)
        # In C#, it iterates `variables`.
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
            
            # C#: string bitString = op_code + BitArrayExtensions.FromInt(value, 16 - op_code.Length).ToBitString();
            operand_bits = BitArray.from_int(value, 16 - len(op_code)).to_bit_string()
            full_bit_string = op_code + operand_bits
            
            mp.set_cell(current_address, BitArray.from_bit_string(full_bit_string))
            current_address += 1

        # Write variables at the end
        for identifier, value in variables.items():
            mp.set_cell(symbols[identifier], BitArray.from_int(value, 16))