from __future__ import annotations

from typing import ClassVar

from src.isa.main import Command, Opcode


class Code:
    # Data memory
    strings: ClassVar[list[str]]
    variables: ClassVar[dict[str, [int, bool]]] = {}

    # Instruction memory
    start: ClassVar[int] = -1
    not_function: ClassVar[bool] = True
    commands: ClassVar[list[Command]] = []
    functions: ClassVar[dict[str, dict[str, str | int]]] = {}
    if_buf: ClassVar[list[Command]] = []
    else_buf: ClassVar[list[Command]] = []
    mode: ClassVar[str] = ""

    @staticmethod
    def add_command(command: Command):
        if Code.mode == "":
            Code.commands.append(command)
        elif Code.mode == "if":
            Code.if_buf.append(command)
        elif Code.mode == "else":
            Code.else_buf.append(command)

    @staticmethod
    def add_str(string: str):
        Code.strings.append(string)

    @staticmethod
    def add_var(name: str, is_str: bool = False) -> None:
        if name not in Code.variables:
            Code.variables[name] = [len(Code.variables), is_str]

    @staticmethod
    def get_var(name: str) -> int:
        assert name in Code.variables, f"Variable {name} not found"
        return Code.variables[name]

    @staticmethod
    def defun(name, args: list):
        Code.functions[name.value] = {"addr": len(Code.commands), "args": []}
        for arg in args:
            Code.functions[name.value]["args"].append(arg.value)

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
                command.arg = command.link_cmd.index
            if command.link_int:
                command.arg = Code.get_var(command.link_int)[0]

            if not command.is_literal_arg:
                command.arg += 1
        return [cmd.to_json() for cmd in Code.commands], []
