import pytest
import os
from src.mic1.control_store import CtrlStoreTxtSrcFileLoader, ControlStore
from src.components.signals import SignalSender
from src.mic1.exceptions.control_store_exceptions import CtrlStoreSrcFileInvalidLineException

# Fixture para criar arquivo temporário
@pytest.fixture
def sample_control_store_file(tmp_path):
    d = tmp_path / "mic1"
    d.mkdir()
    p = d / "control_store_test.txt"
    p.write_text("0: 00000000000000000000000000000000\n10: 11110000000000000000000000001111")
    return str(p)

def test_loader_success(sample_control_store_file):
    # Setup Memory
    addr_sender = SignalSender(0)
    store = ControlStore(addr_sender, SignalSender(0), SignalSender(0), None)
    
    loader = CtrlStoreTxtSrcFileLoader(sample_control_store_file)
    loader.load(store)
    
    # Check Address 0 (All zeros)
    assert store.cell(0).to_bit_string() == "00000000000000000000000000000000"
    # Check Address 10
    assert store.cell(10).to_bit_string() == "11110000000000000000000000001111"

def test_loader_invalid_format(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("InvalidLineWithoutColon")
    
    store = ControlStore(SignalSender(0), SignalSender(0), SignalSender(0), None)
    loader = CtrlStoreTxtSrcFileLoader(str(f))
    
    with pytest.raises(CtrlStoreSrcFileInvalidLineException) as excinfo:
        loader.load(store)
    assert "no ':' were found" in str(excinfo.value)

def test_loader_file_not_found():
    loader = CtrlStoreTxtSrcFileLoader("non_existent.txt")
    store = ControlStore(SignalSender(0), SignalSender(0), SignalSender(0), None)
    with pytest.raises(FileNotFoundError):
        loader.load(store)

if __name__ == "__main__":
    pytest.main()