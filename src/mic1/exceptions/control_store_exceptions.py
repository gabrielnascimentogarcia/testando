class CtrlStoreSrcFileInvalidLineException(Exception):
    def __init__(self, message, line_number=None, inner=None):
        if line_number is not None:
            super().__init__(f"Invalid line on Control Store source file (line {line_number}): {message}")
        else:
            super().__init__(message)
        self.line_number = line_number
        self.inner = inner