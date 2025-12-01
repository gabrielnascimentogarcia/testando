import os
from typing import Optional
from src.components.memory import Memory
from src.components.signals import ISignalSender
from src.utils.bit_utils import BitArray

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
        
        with open(self._source_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                index, bits = self._interpret_line(line)
                memory.set_cell(index, bits)

    def _interpret_line(self, line: str):
        parts = line.replace(" ", "").split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid line: '{line}'")
        
        index = int(parts[0])
        bits = BitArray.from_bit_string(parts[1])
        return index, bits