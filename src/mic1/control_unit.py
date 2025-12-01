from src.components.signals import ISignalSender, SignalSender
from src.components.clock import Clock
from src.components.register import Register
from src.components.multiplexer import Multiplexer
from src.components.processed_signals import ProcessedSignalSender
from src.mic1.control_store import ControlStore, CtrlStoreTxtSrcFileLoader
from src.mic1.mi_register import MIRegister
from src.mic1.flags_register import FlagsRegister

class ControlUnit:
    def __init__(self, in_n: ISignalSender, in_z: ISignalSender, clock: Clock, mir: MIRegister):
        self.clock = clock
        self.mir = mir
        self._flags = FlagsRegister(in_n, in_z, self.mir.out_cond)
        self.mpc = Register(8, name="MPC")
        self._mpc_increment = ProcessedSignalSender.increment(self.mpc.out_sig)
        self._m_mux = Multiplexer(8, [self._mpc_increment, self.mir.out_addr], self._flags.out_sig)

        self.mpc.set_data_sender(self._m_mux.out_sig)
        self.mpc.set_control_sender(self.clock.signal(3))

        self.control_store = ControlStore(self.mpc.out_sig, SignalSender(0), self.clock.signal(0), None)
        
        # Loader expects file relative to execution or fixed path. 
        # Using local path assumption for now.
        loader = CtrlStoreTxtSrcFileLoader("src/mic1/control_store.txt") 
        try:
            loader.load(self.control_store)
        except FileNotFoundError:
            print("WARNING: control_store.txt not found at src/mic1/control_store.txt. Running without microcode.")

        self.mir.set_data_sender(self.control_store.out_sig)
        self.mir.set_control_sender(self.clock.signal(0))

    def reset(self):
        self.clock.reset()
        self.mir.reset()
        self.mpc.reset()