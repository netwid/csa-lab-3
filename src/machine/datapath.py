from __future__ import annotations


class DataPath:
    def __init__(self, data: list[int], size: int, stdin: str):
        self.AR = 0
        self.DR = 0
        self.SP = 0

        self.data = data[:size] + [0]*(size - len(data))
        self.stdin = stdin
