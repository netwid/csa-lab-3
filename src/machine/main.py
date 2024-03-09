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
            logging.debug("Instr: %3d Ticks: %4d IP: %3d Acc: %10d AR: %4d DR: %4d SP: %4d",
                          instr_counter, control_unit.ticks, control_unit.IP, control_unit.data_path.ACC,
                          control_unit.data_path.AR, control_unit.data_path.DR, control_unit.data_path.SP)

            control_unit.process_instruction()
            instr_counter += 1
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")

    return data_path.stdout, data_path.logs


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

    with open(args.input_file) as f:
        stdin = f.read()

    emulate(commands, data, stdin, 5000)



