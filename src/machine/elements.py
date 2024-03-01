from enum import Enum
from typing import ClassVar


class AluOp(Enum):
    pass


class MUX:
    inputs: ClassVar[list] = []

    def in_(self, val):
        self.inputs.append(val)

    def sel(self, index):
        pass


class DEMUX:
    pass
