from __future__ import annotations

import json
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum


class Opcode(str, Enum):
    LOAD = "load"
    STORE = "store"
    PUSH = "push"
    POP = "pop"
    CALL = "call"
    RET = "ret"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    JMP = "jmp"
    CMP = "cmp"
    JE = "je"
    JA = "ja"
    JB = "jb"
    IN = "in"
    OUT = "out"
    NOP = "nop"
    HALT = "halt"

    def __str__(self):
        return str(self.value)


@dataclass
class Command:
    opcode: Opcode
    is_literal_arg: bool = False
    arg: int = 0
    index: int = 0

    # Temp before compile
    link_const_string: int = 0
    link_int: str = None
    link_cmd: Command = None

    comment: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "index": self.index, "opcode": self.opcode.value, "is_literal_arg": self.is_literal_arg, "arg": self.arg,
            "comment": self.comment
        })


class Term(namedtuple("Term", "line pos symbol")):
    """Описание выражения из исходного текста программы.

    Сделано через класс, чтобы был docstring.
    """


def write_code(filename, code):
    """Записать машинный код в фай л."""
    with open(filename, "w", encoding="utf-8") as file:
        # Почему не: `file.write(json.dumps(code, indent=4))`?
        # Чтобы одна инструкция была на одну строку.
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(code: list[dict]) -> list[Command]:
    commands = []

    for cmd in code:
        commands.append(Command(Opcode(cmd["opcode"]), cmd["is_literal_arg"], cmd["arg"]))

    return commands
