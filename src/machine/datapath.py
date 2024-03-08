from __future__ import annotations

from src.machine.elements import ALU


class DataPath:
    def __init__(self, data: list[int], size: int, stdin: str):
        self.ACC = 0
        self.AR = 0
        self.DR = 0
        self.SP = 0
        self.ALU = ALU()

        self.data = data[:size] + [0]*(size - len(data))
        self.stdin = stdin
        self.stdout = ""
        self.logs = []

    def latch_dr(self):
        pass
