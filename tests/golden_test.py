import json
import logging

import pytest
from src.isa.main import read_code
from src.machine.main import emulate
from src.translator.main import translate


@pytest.mark.golden_test("../golden/*.yaml")
def test_emulator(golden, caplog) -> None:
    caplog.set_level(logging.DEBUG)
    instruction_memory, data_memory = translate(golden["source"])
    commands = read_code(json.loads(instruction_memory))
    data_memory = json.loads(data_memory)
    output, log = emulate(commands, data_memory, golden["input"], 5000)
    assert instruction_memory == golden.out["code"]
    assert output == golden.out["output"]
    assert caplog.text == golden.out["log"]
