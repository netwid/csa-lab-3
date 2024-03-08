from __future__ import annotations

import sys
from dataclasses import dataclass

from lark import Lark, Token, Transformer, ast_utils, v_args
from lark.tree import Meta
from src.isa.main import AddressingMode, Command, Opcode
from src.translator.code import Code


class _Ast(ast_utils.Ast):
    def generate(self):
        raise NotImplementedError


class _Expression(_Ast):
    pass


@dataclass
class Program(_Ast, ast_utils.AsList, ast_utils.WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def generate(self):
        [e.generate() for e in self.expressions]


class _Atomic(_Expression):
    pass


@dataclass
class _Integer(_Atomic, ast_utils.WithMeta):
    meta: Meta
    integer: int

    def generate(self):
        Code.add_command(Command(Opcode.LOAD, addressing_mode=AddressingMode.Immediate, arg=self.integer))


@dataclass
class String(_Atomic, ast_utils.WithMeta):
    meta: Meta
    value: str
    idx: int = 0

    def generate(self):
        assert True is all(32 <= ord(char) <= 126 for char in self.value), \
            f"String {self.value} contains invalid characters"
        self.idx = Code.add_str(self.value)
        Code.add_command(Command(Opcode.LOAD, addressing_mode=AddressingMode.Immediate, link_str=self.idx))


@dataclass
class Name(_Atomic, ast_utils.WithMeta):
    meta: Meta
    value: str

    def generate(self):
        Code.add_command(Command(Opcode.LOAD, addressing_mode=AddressingMode.StackRelative,
                                 arg=Code.get_var_addr(Code.current_function, self.value)))


@dataclass
class Args(_Ast, ast_utils.AsList, ast_utils.WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def generate(self) -> None:
        for expression in self.expressions[1:][::-1]:
            expression.generate()
            Code.push()
        self.expressions[0].generate()


@dataclass
class Invokable(_Ast, ast_utils.WithMeta):
    meta: Meta
    invokable: str | Name

    def generate(self):
        print("Invokable {}".format(self.invokable))


def check_args_len(invokable: str, args: list[_Expression], need_len: int):
    assert len(args) == need_len, f"{invokable} take {need_len} arguments but {len(args)} were given"


def bin_op(name: str, opcode: Opcode, args: list[_Expression]):
    check_args_len(name, args, 2)
    Code.add_command(Command(opcode, addressing_mode=AddressingMode.StackRelative, arg=1))
    Code.pop()


def jump_op(opcodes: list[Opcode]):
    Code.add_command(Command(Opcode.CMP, addressing_mode=AddressingMode.StackRelative, arg=1))
    Code.pop()
    for opcode in opcodes:
        Code.add_command(Command(opcode, link_addr=Code.if_stack[-1]["if_body_addr"]))
    Code.add_command(Command(Opcode.JMP, link_addr=Code.if_stack[-1]["else_body_addr"]))


@dataclass
class Invoke(_Expression, ast_utils.WithMeta):
    meta: Meta
    invokable: Invokable
    args: Args

    def generate(self):
        index = len(Code.commands)

        if Code.current_function == "" and Code.start == -1:
            Code.start = index

        match self.invokable.invokable:
            case "+":
                self.args.generate()
                bin_op("+", Opcode.ADD, self.args.expressions)
            case "-":
                self.args.generate()
                bin_op("-", Opcode.SUB, self.args.expressions)
            case "*":
                self.args.generate()
                bin_op("*", Opcode.MUL, self.args.expressions)
            case "/":
                self.args.generate()
                bin_op("/", Opcode.DIV, self.args.expressions)
            case "%":
                self.args.generate()
                bin_op("%", Opcode.MOD, self.args.expressions)
            case "set":
                invoke_set(self.args)
            case "read":
                pass
            case "print":
                self.args.generate()
                idx = self.args.expressions[0].idx
                Code.add_command(Command(Opcode.ADD, addressing_mode=AddressingMode.Immediate, arg=1))
                Code.add_command(Command(Opcode.STORE))

                out = Command(Opcode.OUT, addressing_mode=AddressingMode.Indirect, arg=0)
                Code.add_command(out)
                Code.add_command(Command(Opcode.LOAD))
                Code.add_command(Command(Opcode.ADD, addressing_mode=AddressingMode.Immediate, arg=1))
                Code.add_command(Command(Opcode.STORE))

                Code.add_command(Command(Opcode.LOAD, link_str=idx))
                Code.add_command(Command(Opcode.CMP, addressing_mode=AddressingMode.Immediate, arg=1))
                Code.add_command(Command(Opcode.JE, arg=len(Code.commands)+4))
                Code.add_command(Command(Opcode.SUB, addressing_mode=AddressingMode.Immediate, arg=1))
                Code.add_command(Command(Opcode.STORE, link_str=idx))
                Code.add_command(Command(Opcode.JMP, link_cmd=out))
            case "=":
                self.args.generate()
                jump_op([Opcode.JE])
            case "<":
                self.args.generate()
                jump_op([Opcode.JE, Opcode.JA])
            case ">":
                self.args.generate()
                jump_op([Opcode.JE, Opcode.JB])
            case _:
                name = self.invokable.invokable.value
                assert name in Code.functions, f"function {name} don't exists"

                args_num = len(Code.functions[name]["args"])
                assert len(self.args.expressions) == args_num, \
                    f"function {name} take {args_num} arguments, {len(self.args.expressions)} passed"

                self.args.generate()
                Code.push()
                Code.add_command(Command(Opcode.CALL, arg=Code.functions[name]["addr"]))
                for _ in range(len(self.args.expressions)):
                    Code.pop()


def invoke_set(args: Args):
    assert len(args.expressions) == 2

    name, value = args.expressions
    assert name.__class__ == Name
    value.generate()

    Code.pop()
    Code.add_var(name.value)
    Code.add_command(Command(Opcode.STORE, link_int=name.value))


@dataclass
class Condition(_Ast, ast_utils.WithMeta):
    meta: Meta
    expression: _Expression

    def generate(self):
        self.expression.generate()


@dataclass
class IfBody(_Ast, ast_utils.WithMeta):
    meta: Meta
    expression: _Expression

    def generate(self):
        self.expression.generate()


@dataclass
class ElseBody(_Ast, ast_utils.WithMeta):
    meta: Meta
    expression: _Expression

    def generate(self):
        self.expression.generate()


@dataclass
class IfExpression(_Expression, ast_utils.WithMeta):
    meta: Meta
    condition: Condition
    if_body: IfBody
    else_body: ElseBody = None

    def generate(self):
        Code.if_stack.append({"pushes": 0, "if_body_addr": [0], "else_body_addr": [0], "end_if": [0]})

        self.condition.generate()
        Code.if_stack[-1]["pushes"] = Code.pushes
        Code.if_stack[-1]["if_body_addr"][0] = len(Code.commands)
        self.if_body.generate()
        Code.pushes = Code.if_stack[-1]["pushes"]
        Code.add_command(Command(Opcode.JMP, link_addr=Code.if_stack[-1]["end_if"]))
        Code.if_stack[-1]["else_body_addr"][0] = len(Code.commands)
        self.else_body.generate()
        Code.if_stack[-1]["end_if"][0] = len(Code.commands)
        Code.pushes = Code.if_stack[-1]["pushes"]

        Code.if_stack = Code.if_stack[:-1]


@dataclass
class Params(_Ast, ast_utils.AsList, ast_utils.WithMeta):
    meta: Meta
    names: list[Name]

    def generate(self):
        pass


@dataclass
class Body(_Ast, ast_utils.WithMeta):
    meta: Meta
    expression: _Expression

    def generate(self):
        self.expression.generate()


@dataclass
class Function(_Expression, ast_utils.WithMeta):
    meta: Meta
    name: Name
    params: Params
    body: Body

    def generate(self):
        Code.current_function = self.name.value
        Code.defun(self.name, self.params.names)
        Code.add_command(Command(Opcode.NOP, comment=f"defun {self.name.value}"))
        self.body.generate()
        Code.add_command(Command(Opcode.RET))
        Code.current_function = ""


class ToAst(Transformer):
    def NAME(self, token: Token) -> str:  # noqa: N802
        return token.value

    def STRING(self, token: Token) -> str:  # noqa: N802
        return token.value[1:-1]

    @v_args(meta=True)
    def integer(self, meta: Meta, tokens: list[Token]) -> _Integer:
        number = int(tokens[0].value)
        return _Integer(meta, number)

    @v_args(inline=True)
    def expression(self, tree: _Expression) -> _Expression:
        return tree

    @v_args(inline=True)
    def atomic(self, tree: _Atomic) -> _Atomic:
        return tree

    @v_args(inline=True)
    def start(self, tree: Program) -> Program:
        return tree


parser = Lark.open("grammar.lark", rel_to=__file__, start="program")
transformer = ast_utils.create_transformer(sys.modules[__name__], ToAst())


def parse(text: str) -> _Ast:
    tree = parser.parse(text)
    return transformer.transform(tree)
