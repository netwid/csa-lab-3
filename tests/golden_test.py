import pytest
from src.machine.main import emulate
from src.translator.main import translate


@pytest.mark.golden_test("./../golden/*.yaml")
def test_emulator(golden) -> None:
    instruction_memory, data_memory = translate(golden["source"])
    output, log = emulate(instruction_memory, data_memory, golden["input"], 1000)
    assert instruction_memory == golden.out["code"]
    assert output == golden.out["output"]
    assert log == golden.out["log"]
