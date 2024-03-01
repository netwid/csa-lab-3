from __future__ import annotations

import argparse
import json
import logging

from src.isa.main import Command, read_code
from src.machine.control_unit import ControlUnit
from src.machine.datapath import DataPath


def emulate(commands: list[Command], data: list[int], stdin: str, limit: int) -> (str, str):
    data_path = DataPath(data, 500, stdin)
    control_unit = ControlUnit(commands, data_path)

    instr_counter = 0

    try:
        while instr_counter < limit:
            logging.debug("Acc: %d, SP: %d, IP: %d", control_unit.acc, control_unit.sp, control_unit.ip)

            control_unit.decode_and_execute_instruction()
            instr_counter += 1

            logging.debug("data[490:]: %s", control_unit.data_path.data[490:])
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(description="Machine emulator")
    parser.add_argument("code_data_file", type=str)
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    with open(args.code_data_file) as f:
        content = json.load(f)
    code, data = content["instruction_memory"], content["data_memory"]

    commands = read_code(code)

    emulate(commands, data, "", 1000)



