from src.components.register import Register
from src.components.processed_signals import ProcessedSignalSender

class MIRegister(Register):
    def __init__(self):
        super().__init__(32)
        
        self.out_a_mux    = ProcessedSignalSender.interval(self.out_sig, 31, 1)
        self.out_cond     = ProcessedSignalSender.interval(self.out_sig, 29, 2)
        self.out_alu      = ProcessedSignalSender.interval(self.out_sig, 27, 2)
        self.out_shifter  = ProcessedSignalSender.interval(self.out_sig, 25, 2)
        self.out_mbr      = ProcessedSignalSender.interval(self.out_sig, 24, 1)
        self.out_mar      = ProcessedSignalSender.interval(self.out_sig, 23, 1)
        self.out_rd       = ProcessedSignalSender.interval(self.out_sig, 22, 1)
        self.out_wr       = ProcessedSignalSender.interval(self.out_sig, 21, 1)
        self.out_enc      = ProcessedSignalSender.interval(self.out_sig, 20, 1)
        self.out_c        = ProcessedSignalSender.interval(self.out_sig, 16, 4)
        self.out_b        = ProcessedSignalSender.interval(self.out_sig, 12, 4)
        self.out_a        = ProcessedSignalSender.interval(self.out_sig, 8, 4)
        self.out_addr     = ProcessedSignalSender.interval(self.out_sig, 0, 8)