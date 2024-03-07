from __future__ import annotations

from typing import ClassVar

from src.isa.main import AddressingMode, Command, Opcode


class Code:
    # Data memory
    strings: ClassVar[list[str]]
    variables: ClassVar[dict[str, [int, bool]]] = {}

    # Instruction memory
    start: ClassVar[int] = -1
    current_function: ClassVar[str] = ""
    commands: ClassVar[list[Command]] = []
    functions: ClassVar[dict[str, dict[str, str | int | dict]]] = {}
    if_stack: ClassVar[list[dict]] = []
    pushes: ClassVar[int] = 0

    @staticmethod
    def add_command(command: Command):
        Code.commands.append(command)

    @staticmethod
    def push():
        Code.pushes += 1
        Code.add_command(Command(Opcode.PUSH))

    @staticmethod
    def pop():
        Code.pushes -= 1
        Code.add_command(Command(Opcode.POP))

    @staticmethod
    def add_str(string: str):
        Code.strings.append(string)

    @staticmethod
    def add_var(name: str, is_str: bool = False) -> None:
        if name not in Code.variables:
            Code.variables[name] = [len(Code.variables), is_str]

    @staticmethod
    def get_var_addr(fun: str, name: str) -> int:
        assert name in Code.functions[fun]["args"], f"Variable {name} not found"
        return Code.functions[fun]["args"][name] + 2 + Code.pushes

    @staticmethod
    def defun(name, args: list):
        Code.pushes = 0
        Code.functions[name.value] = {"addr": len(Code.commands), "args": {}}
        for arg in args:
            Code.functions[name.value]["args"][arg.value] = len(Code.functions[name.value]["args"])
        print(Code.functions)

    @staticmethod
    def place_data():
        index = 1
        for var in Code.variables.values():
            var[0] = index
            index += 1

    @staticmethod
    def compile() -> (list[str], list):
        Code.place_data()
        Code.commands = [Command(Opcode.JMP, arg=Code.start), *Code.commands]
        Code.commands.append(Command(Opcode.HALT))
        for index, command in enumerate(Code.commands):
            command.index = index
        for _, command in enumerate(Code.commands):
            if command.link_cmd:
                command.arg = command.link_cmd.index - 1
            if command.link_int:
                command.arg = Code.get_var(command.link_int)[0]
            if command.link_addr:
                command.arg = command.link_addr[0]

            if (not command.addressing_mode == AddressingMode.Immediate
                    and not command.addressing_mode == AddressingMode.StackRelative):
                command.arg += 1
        return [cmd.to_json() for cmd in Code.commands], []
