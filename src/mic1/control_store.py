import os
from typing import Optional, Tuple
from src.components.memory import Memory
from src.components.signals import ISignalSender
from src.utils.bit_utils import BitArray
from src.mic1.exceptions.control_store_exceptions import CtrlStoreSrcFileInvalidLineException

class ControlStore(Memory):
    def __init__(self, address_sender: ISignalSender, in_buffer_sender: ISignalSender,
                 rd_sender: Optional[ISignalSender], wr_sender: Optional[ISignalSender]):
        super().__init__(256, 32, address_sender, in_buffer_sender, rd_sender, wr_sender, None)

class CtrlStoreTxtSrcFileLoader:
    def __init__(self, source_file_path: str):
        self._source_file_path = source_file_path

    def load(self, memory: Memory):
        if not os.path.exists(self._source_file_path):
            raise FileNotFoundError(f"control store source file not found: {self._source_file_path}")
        
        with open(self._source_file_path, 'r', encoding='utf-8') as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line: continue
                
                # C# logic uses 0-based index for logic but exception might use 1-based or 0-based?
                # C# Code: lineIndex++; in loop. Exception uses lineIndex.
                # Let's assume 1-based for user friendliness or match C# variable 'lineIndex' which usually starts at 0?
                # C#: int lineIndex = 0; ... lineIndex++;
                # So the first line is index 0.
                
                try:
                    index, bits = self._interpret_line(line)
                    memory.set_cell(index, bits)
                except Exception as e:
                    # Wrap generic errors if they aren't already our custom exception?
                    # The C# code throws CtrlStoreSrcFIleInvalidLineException directly in InterpretLine.
                    if isinstance(e, CtrlStoreSrcFileInvalidLineException):
                        raise e
                    # Else re-raise or wrap? C# doesn't catch in Load, so it propagates.
                    raise e

    def _interpret_line(self, line: str) -> Tuple[int, BitArray]:
        # C#: string[] parts = line.Replace(" ", "").Split(":");
        clean_line = line.replace(" ", "")
        parts = clean_line.split(":")

        if len(parts) == 1:
            raise CtrlStoreSrcFileInvalidLineException(
                f"Invalid line: no ':' were found. Content: '{line}'"
            )
        
        if len(parts) != 2:
            raise CtrlStoreSrcFileInvalidLineException(
                f"Invalid line: more than one ':' were found on a single line. Content: '{line}'"
            )

        try:
            index = int(parts[0])
            bits = BitArray.from_bit_string(parts[1])
            return index, bits
        except ValueError as ve:
             raise CtrlStoreSrcFileInvalidLineException(f"Parse error: {ve}")