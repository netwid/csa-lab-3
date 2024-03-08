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
        self.ticks = 0

    def instr_fetch(self) -> None:
        self.latch_cr()
        self.latch_ip(Selector.FROM_IP)
        self.tick()

    def latch_cr(self):
        self.CR = self.commands[self.IP]

    def latch_ip(self, sel: Selector):
        if sel == Selector.FROM_IP:
            self.IP += 1
        if sel == Selector.FROM_CR:
            self.IP = self.CR.arg
        if sel == Selector.FROM_DR:
            self.IP = self.data_path.DR

    def operand_fetch(self) -> None:
        if self.CR.addressing_mode == AddressingMode.Immediate:
            self.data_path.latch_dr(Selector.FROM_CR, self.CR.arg)
            self.tick()
        if self.CR.addressing_mode in [AddressingMode.Direct, AddressingMode.Indirect]:
            self.data_path.latch_ar(Selector.FROM_CR, self.CR.arg)
            self.tick()
        if self.CR.addressing_mode == AddressingMode.Indirect:
            self.data_path.latch_ar(Selector.FROM_MEMORY)
            self.tick()
        if self.CR.addressing_mode == AddressingMode.StackRelative:
            self.data_path.latch_ar(Selector.FROM_RELATIVE_SP, self.data_path.SP + self.CR.arg)
        if (self.CR.addressing_mode in [AddressingMode.Direct, AddressingMode.Indirect, AddressingMode.StackRelative]
                and self.CR.opcode != Opcode.STORE):
            self.data_path.signal_oe()
            self.tick()

    def execute_instruction(self):
        command = self.CR

        match command.opcode:
            case Opcode.HALT:
                raise StopIteration
            case Opcode.PUSH:
                self.data_path.data[self.data_path.SP] = self.data_path.ACC
                self.data_path.latch_sp(Selector.SEL_DEC)
            case Opcode.POP:
                self.data_path.latch_sp(Selector.SEL_INC)
            case Opcode.LOAD:
                self.data_path.latch_right()
                self.data_path.alu_eval(Opcode.ADD)
                self.data_path.latch_acc()
            case Opcode.STORE:
                self.data_path.latch_ar(Selector.FROM_CR, command.arg)
                self.data_path.latch_dr(Selector.FROM_ACC)
                self.data_path.signal_wr()
            case Opcode.ADD | Opcode.SUB | Opcode.MUL | Opcode.DIV | Opcode.MOD | Opcode.CMP:
                self.data_path.latch_left()
                self.data_path.latch_right()
                self.data_path.alu_eval(command.opcode)
                if command.opcode != Opcode.CMP:
                    self.data_path.latch_acc()
            case Opcode.JMP:
                self.latch_ip(Selector.FROM_CR)
            case Opcode.JE:
                if self.data_path.ALU.get_flags()["z"]:
                    self.latch_ip(Selector.FROM_CR)
            case Opcode.JA:
                if not self.data_path.ALU.get_flags()["z"] and not self.data_path.ALU.get_flags()["c"]:
                    self.latch_ip(Selector.FROM_CR)
            case Opcode.JB:
                if self.data_path.ALU.get_flags()["c"]:
                    self.latch_ip(Selector.FROM_CR)
            case Opcode.CALL:
                self.data_path.latch_dr(Selector.FROM_IP, self.IP)
                self.data_path.latch_ar(Selector.FROM_SP)
                self.data_path.signal_wr()
                self.data_path.latch_sp(Selector.SEL_DEC)
                self.latch_ip(Selector.FROM_CR)
            case Opcode.RET:
                self.data_path.latch_sp(Selector.SEL_INC)
                self.data_path.latch_ar(Selector.FROM_SP)
                self.data_path.signal_oe()
                self.latch_ip(Selector.FROM_DR)
            case Opcode.OUT:
                self.data_path.stdout += chr(self.data_path.data[self.data_path.data[command.arg]])
            case Opcode.OUT_INT:
                self.data_path.stdout += str(self.data_path.ACC)

    def process_instruction(self):
        self.instr_fetch()
        non_addr_command = [

        ]
        if self.CR.opcode not in non_addr_command:
            self.operand_fetch()
        self.execute_instruction()

    def tick(self) -> None:
        self.ticks += 1
