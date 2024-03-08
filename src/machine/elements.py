from __future__ import annotations

from enum import Enum, auto

from src.isa.main import Opcode


class Selector(Enum):
    FROM_DR = auto()
    FROM_PORT = auto()
    FROM_MEMORY = auto()
    FROM_ACC = auto()
    FROM_ALU = auto()
    SEL_INC = auto()
    SEL_DEC = auto()
    FROM_IP = auto()
    FROM_CR = auto()
    FROM_AR = auto()
    FROM_SP = auto()
    FROM_INPUT = auto()
    TO_INPUT = auto()
    FROM_RELATIVE_SP = auto


class ALU:
    def __init__(self):
        self.Z = 0
        self.C = 0
        self.result: int = 0

    def eval(self, opcode: Opcode, left: int, right: int):
        self.result = 0
        match opcode:
            case Opcode.ADD:
                self.result = left + right
            case Opcode.SUB:
                self.result = left - right
            case Opcode.MUL:
                self.result = left * right
            case Opcode.DIV:
                self.result = left // right
            case Opcode.MOD:
                self.result = left % right
            case Opcode.CMP:
                self.result = left - right

        self.set_flags()

    def set_flags(self):
        self.Z = self.result == 0
        self.C = self.result < 0

    def get_flags(self) -> dict[str, int]:
        return {"z": self.Z, "c": self.C}

