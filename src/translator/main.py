#!/usr/bin/python3
"""Транслятор LISP в машинный код.
"""
from __future__ import annotations

import argparse

from src.translator.ast import parse
from src.translator.code import Code


def translate(text) -> (str, str):
    tree = parse(text)
    tree.generate()
    code, data = Code.compile()
    return "[" + ",\n ".join(code) + "]", "[" + ",\n ".join(data) + "]"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lisp translator")
    parser.add_argument("input_file", type=str)
    parser.add_argument("output_file", type=str)
    args = parser.parse_args()

    with open(args.input_file) as input_file:
        with open(args.output_file, "w") as output_file:
            code, data = translate(input_file.read())
            output_file.write(f'{{\n    "instruction_memory": {code},\n    "data_memory": {data}\n}}')
