from __future__ import annotations

from typing import ClassVar

from src.isa.main import Command, Opcode


class Code:
    # Data memory
    strings: ClassVar[list[list[str | int]]] = []
    variables: ClassVar[dict[str, [int, bool]]] = {}
    data: ClassVar[list] = [0] * 500
    inputs: ClassVar[list[list[int], list[int]]] = []
    last_input: list[int] = None

    # Instruction memory
    start: ClassVar[int] = -1
    current_function: ClassVar[str] = ""
    commands: ClassVar[list[Command]] = []
    functions: ClassVar[dict[str, dict[str, str | int | dict]]] = {}
    if_stack: ClassVar[list[dict]] = []
    pushes: ClassVar[int] = 0

    @staticmethod
    def clear():
        Code.commands = []
        Code.strings = []
        Code.variables = {}
        Code.data = [0] * 500
        Code.start = -1
        Code.current_function = ""
        Code.functions = {}
        Code.if_stack = []
        Code.pushes = 0
        Code.last_input = None

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
    def add_str(string: str) -> int:
        Code.strings.append([string, 0])
        return len(Code.strings) - 1

    @staticmethod
    def add_input():
        Code.inputs.append([[0], [0]])
        return Code.inputs[-1]

    @staticmethod
    def add_var(name: str, is_str: bool = False) -> None:
        if name not in Code.variables:
            Code.variables[name] = [len(Code.variables), is_str]

    @staticmethod
    def get_var(name: str, is_str: bool = False) -> None:
        pass

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

    @staticmethod
    def place_data():
        index = 3
        for var in Code.variables.values():
            var[0] = index
            index += 1
        for s in Code.strings:
            s[1] = index
            Code.data[index] = len(s[0])
            index += 1
            for char in s[0]:
                Code.data[index] = ord(char)
                index += 1
        for i in Code.inputs:
            Code.data[index] = index + 2
            i[0][0] = index
            i[1][0] = index + 1
            index += 100

    @staticmethod
    def compile() -> (list[str], list):
        Code.place_data()
        Code.commands[0].arg = Code.start
        Code.commands.append(Command(Opcode.HALT))
        for index, command in enumerate(Code.commands):
            command.index = index
        for _, command in enumerate(Code.commands):
            if command.link_cmd:
                command.arg = command.link_cmd.index
            if command.link_int:
                command.arg = Code.get_var(command.link_int)[0]
            if command.link_addr:
                command.arg = command.link_addr[0]
            if command.link_str != -1:
                command.arg = Code.strings[command.link_str][1]

        return [cmd.to_json() for cmd in Code.commands], Code.data
