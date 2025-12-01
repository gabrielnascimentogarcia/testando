class AssemblerV2Exception(Exception):
    def __init__(self, message, inner=None):
        super().__init__(message)
        self.inner = inner

class SyntaxErrorException(AssemblerV2Exception):
    def __init__(self, line_number, line):
        super().__init__(f"SyntaxError on the line {line_number}: {line}")
        self.line_number = line_number

class DuplicatedSymbolException(AssemblerV2Exception):
    def __init__(self, line_number, symbol):
        super().__init__(f"Duplicated declaration of the symbol '{symbol}' on the line {line_number}")
        self.line_number = line_number
        self.symbol = symbol

class SymbolNotDefinedException(AssemblerV2Exception):
    def __init__(self, line_number, symbol):
        super().__init__(f"Use of undefined symbol '{symbol}' on the line {line_number}")
        self.line_number = line_number
        self.symbol = symbol

class OpCodeNotDefinedException(AssemblerV2Exception):
    def __init__(self, line_number, op_code):
        super().__init__(f"OpCode '{op_code}' not defined on the line {line_number}")
        self.line_number = line_number
        self.op_code = op_code