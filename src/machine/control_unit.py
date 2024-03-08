from __future__ import annotations

from src.isa.main import AddressingMode, Command, Opcode
from src.machine.datapath import DataPath
from src.machine.elements import Selector


class ControlUnit:
    def __init__(self, commands: list[Command], data_path: DataPath):
        self.commands = commands
        self.data_path = data_path
        self.CR: Command | None = None
        self.IP = 0
        self.SP = len(self.data_path.data) - 1
        self.ACC = 0
        self.z = False
        self.c = False

    def latch_ip(self, sel: Selector):
        if sel == Selector.FROM_IP:
            self.IP += 1
        if sel == Selector.FROM_CR:
            self.IP = self.CR.arg

    def latch_cr(self):
        self.CR = self.commands[self.IP]

    def decode_and_execute_instruction(self):  # noqa: C901
        command = self.commands[self.IP]

        match command.opcode:
            case Opcode.HALT:
                raise StopIteration
            case Opcode.PUSH:
                self.data_path.data[self.SP] = self.ACC
                self.SP -= 1
            case Opcode.POP:
                self.SP += 1
                self.data_path.data[self.SP] = 0  # for testing
            case Opcode.LOAD:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC = command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC = self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC = self.data_path.data[command.arg]
            case Opcode.STORE:
                self.data_path.data[command.arg] = self.ACC
            case Opcode.ADD:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC += command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC += self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC += self.data_path.data[command.arg]
            case Opcode.SUB:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC -= command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC -= self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC -= self.data_path.data[command.arg]
            case Opcode.MUL:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC *= command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC *= self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC *= self.data_path.data[command.arg]
            case Opcode.DIV:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC //= command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC //= self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC //= self.data_path.data[command.arg]
            case Opcode.MOD:
                if command.addressing_mode == AddressingMode.Immediate:
                    self.ACC %= command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    self.ACC %= self.data_path.data[self.SP + command.arg]
                else:
                    self.ACC %= self.data_path.data[command.arg]
            case Opcode.CMP:
                if command.addressing_mode == AddressingMode.Immediate:
                    temp = self.ACC - command.arg
                elif command.addressing_mode == AddressingMode.StackRelative:
                    temp = self.ACC - self.data_path.data[self.SP + command.arg]
                else:
                    temp = self.ACC - self.data_path.data[command.arg]
                self.z = temp == 0
                self.c = temp < 0
            case Opcode.JMP:
                self.IP = command.arg - 1
            case Opcode.JE:
                if self.z:
                    self.IP = command.arg - 1
            case Opcode.JA:
                if not self.z and not self.c:
                    self.IP = command.arg - 1
            case Opcode.JB:
                if self.c:
                    self.IP = command.arg - 1
            case Opcode.CALL:
                self.data_path.data[self.SP] = self.IP
                self.SP -= 1
                self.IP = command.arg - 1
            case Opcode.RET:
                self.IP = self.data_path.data[self.SP + 1]
                self.data_path.data[self.SP + 1] = 0
                self.SP += 1
            case Opcode.OUT:
                self.data_path.stdout += chr(self.data_path.data[self.data_path.data[command.arg]])

        self.IP += 1

