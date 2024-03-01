from __future__ import annotations

import sys
from dataclasses import dataclass

from lark import Lark, Token, Transformer, ast_utils, v_args
from lark.tree import Meta
from src.isa.main import Command, Opcode
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
        Code.add_command(Command(Opcode.LOAD, is_literal_arg=True, arg=self.integer))
        Code.add_command(Command(Opcode.PUSH))


@dataclass
class String(_Atomic, ast_utils.WithMeta):
    meta: Meta
    value: str

    def generate(self):
        assert True is all(32 <= ord(char) <= 126 for char in self.value), \
            f"String {self.value} contains invalid characters"


@dataclass
class Name(_Atomic, ast_utils.WithMeta):
    meta: Meta
    value: str

    def generate(self):
        Code.get_var(self.value)
        Code.add_command(Command(Opcode.LOAD, link_int=self.value))
        Code.add_command(Command(Opcode.PUSH))


@dataclass
class Args(_Ast, ast_utils.AsList, ast_utils.WithMeta):
    meta: Meta
    expressions: list[_Expression]

    def generate(self) -> None:
        [x.generate() for x in self.expressions]


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
    Code.add_command(Command(Opcode.POP))
    Code.add_command(Command(Opcode.STORE))
    Code.add_command(Command(Opcode.POP))
    Code.add_command(Command(opcode))
    Code.add_command(Command(Opcode.PUSH))


def jump_op(opcodes: list[Opcode]):
    nop = Command(Opcode.NOP)
    Code.add_command(Command(Opcode.POP))
    Code.add_command(Command(Opcode.STORE))
    Code.add_command(Command(Opcode.POP))
    Code.add_command(Command(Opcode.CMP))
    for opcode in opcodes:
        Code.add_command(Command(opcode, link_cmd=Code.if_buf[0]))
    if Code.else_buf:
        Code.add_command(Command(Opcode.JMP, link_cmd=Code.else_buf[0]))
    else:
        Code.add_command(Command(Opcode.JMP, link_cmd=nop))
    for code in Code.if_buf:
        Code.add_command(code)
    Code.add_command(Command(Opcode.JMP, link_cmd=nop))
    for code in Code.else_buf:
        Code.add_command(code)
    Code.add_command(nop)
    Code.add_command(Command(Opcode.PUSH))
    Code.if_buf = []
    Code.else_buf = []


@dataclass
class Invoke(_Expression, ast_utils.WithMeta):
    meta: Meta
    invokable: Invokable
    args: Args

    def generate(self):
        index = len(Code.commands)

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
                pass
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

                args_num = len(Code.functions[name]['args'])
                assert len(self.args.expressions) == args_num, \
                    f"function {name} take {args_num} arguments, {len(self.args.expressions)} passed"

                self.args.generate()
                for i in range(args_num):
                    Code.add_command(Command(Opcode.POP))
                    Code.add_command(Command(Opcode.STORE, link_int=Code.functions[name]["args"][args_num-i-1]))
                Code.add_command(Command(Opcode.CALL, arg=Code.functions[name]["addr"]))

        if Code.not_function and Code.start == -1:
            Code.start = index


def invoke_set(args: Args):
    assert len(args.expressions) == 2

    name, value = args.expressions
    assert name.__class__ == Name
    value.generate()

    Code.add_command(Command(Opcode.POP))
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
        Code.not_function = False
        Code.defun(self.name, self.params.names)
        Code.add_command(Command(Opcode.NOP, comment=f"defun {self.name.value}"))
        self.params.generate()
        self.body.generate()
        Code.add_command(Command(Opcode.POP))
        Code.add_command(Command(Opcode.RET))
        Code.not_function = True


@dataclass
class IfExpression(_Expression, ast_utils.WithMeta):
    meta: Meta
    condition: Condition
    if_body: IfBody
    else_body: ElseBody = None

    def generate(self):
        Code.mode = "if"
        self.if_body.generate()
        if self.else_body:
            Code.mode = "else"
            self.else_body.generate()
        Code.mode = ""
        self.condition.generate()


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
