from __future__ import annotations

from src.isa.main import Opcode
from src.machine.elements import ALU, Selector


class DataPath:
    def __init__(self, data: list[int], size: int, stdin: str):
        self.ACC = 0
        self.AR = 0
        self.DR = 0
        self.SP = len(data) - 1
        self.ALU = ALU()

        self.data = data[:size] + [0]*(size - len(data))
        self.stdin = stdin
        self.stdout = ""
        self.logs = []

        self.left = 0
        self.right = 0

    def latch_ar(self, sel: Selector, value: int = 0):
        assert sel in {Selector.FROM_CR, Selector.FROM_SP, Selector.FROM_MEMORY, Selector.FROM_RELATIVE_SP}, \
            f"Selector error, incorrect selector: {sel}"
        if sel == Selector.FROM_CR or sel == Selector.FROM_RELATIVE_SP:
            self.AR = value
        if sel == Selector.FROM_SP:
            self.AR = self.SP
        if sel == Selector.FROM_MEMORY:
            self.AR = self.data[self.AR]

    def latch_dr(self, sel: Selector, value: int = 0):
        assert sel in {Selector.FROM_CR, Selector.FROM_ACC, Selector.FROM_IP}, f"Selector error, incorrect selector: {sel}"
        if sel == Selector.FROM_CR:
            self.DR = value
        if sel == Selector.FROM_IP:
            self.DR = value
        if sel == Selector.FROM_ACC:
            self.DR = self.ACC

    def signal_oe(self):
        self.DR = self.data[self.AR]

    def signal_wr(self):
        self.data[self.AR] = self.DR

    def latch_left(self):
        self.left = self.ACC

    def latch_right(self):
        self.right = self.DR

    def latch_acc(self, sel: Selector = Selector.FROM_ALU):
        if sel == Selector.FROM_ALU:
            self.ACC = self.ALU.result

    def latch_sp(self, sel: Selector):
        if sel == Selector.SEL_INC:
            self.SP += 1
        if sel == Selector.SEL_DEC:
            self.SP -= 1

    def alu_eval(self, opcode: Opcode):
        self.ALU.eval(opcode, self.left, self.right)
        self.left, self.right = 0, 0
