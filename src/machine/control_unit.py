from __future__ import annotations

from src.isa.main import Command, Opcode
from src.machine.datapath import DataPath


class ControlUnit:
    def __init__(self, commands: list[Command], data_path: DataPath):
        self.commands = commands
        self.data_path = data_path
        self.ip = 0
        self.sp = len(self.data_path.data)-1
        self.acc = 0
        self.z = False
        self.c = False

    def decode_and_execute_instruction(self):  # noqa: C901
        command = self.commands[self.ip]

        match command.opcode:
            case Opcode.HALT:
                raise StopIteration
            case Opcode.PUSH:
                self.data_path.data[self.sp] = self.acc
                self.sp -= 1
                pass
            case Opcode.POP:
                self.acc = self.data_path.data[self.sp+1]
                self.sp += 1
                pass
            case Opcode.LOAD:
                if command.is_literal_arg:
                    self.acc = command.arg
                else:
                    self.acc = self.data_path.data[command.arg]
            case Opcode.STORE:
                self.data_path.data[command.arg] = self.acc
            case Opcode.ADD:
                if command.is_literal_arg:
                    self.acc += command.arg
                else:
                    self.acc += self.data_path.data[command.arg]
            case Opcode.SUB:
                if command.is_literal_arg:
                    self.acc -= command.arg
                else:
                    self.acc -= self.data_path.data[command.arg]
            case Opcode.MUL:
                if command.is_literal_arg:
                    self.acc *= command.arg
                else:
                    self.acc *= self.data_path.data[command.arg]
            case Opcode.DIV:
                if command.is_literal_arg:
                    self.acc //= command.arg
                else:
                    self.acc //= self.data_path.data[command.arg]
            case Opcode.MOD:
                if command.is_literal_arg:
                    self.acc %= command.arg
                else:
                    self.acc %= self.data_path.data[command.arg]
            case Opcode.CMP:
                if command.is_literal_arg:
                    temp = self.acc - command.arg
                else:
                    temp = self.acc - self.data_path.data[command.arg]
                if temp == 0:
                    self.z = True
                if temp < 0:
                    self.c = True
            case Opcode.JMP:
                self.ip = command.arg - 1
            case Opcode.JE:
                if self.z:
                    self.ip = command.arg - 1
            case Opcode.JA:
                if not self.z and not self.c:
                    self.ip = command.arg - 1
            case Opcode.JB:
                if self.c:
                    self.ip = command.arg - 1
            case Opcode.CALL:
                self.data_path.data[self.sp] = self.ip
                self.sp -= 1
                self.ip = command.arg - 1
            case Opcode.RET:
                self.ip = self.data_path.data[self.sp+1]
                self.sp += 1

        self.ip += 1

