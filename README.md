# Лабораторная работа №3. Транслятор и модель процессора

- P33111. Кузьмин Илья Дмитриевич
- lisp | acc | harv | hw | instr | struct | stream | port | pstr | prob5 | 8bit (Базовый вариант)
- без усложнения

## Язык программирования
За основу языка взят диалект Common Lisp

### Syntax
```
program: expression+

?expression : atomic
           | if_expression
           | function
           | invoke

atomic : name
       | integer
       | string


function : "(" "defun" name "(" args ")" body ")"
body : expression+

invoke : "(" invokable args ")"
!invokable : "="
    | "+"
    | "-"
    | "*"
    | "/"
    | "%"
    | ">"
    | "<"
    | "<="
    | ">="
    | "set"
    | "read"
    | "print"
    | name

args : expression*
# predefined names: =, +, -, //, %, >, <, <=, >=, set, read, print

if_expression : "(" "if" condition if_body else_body? ")"
condition : expression
if_body : expression
else_body : expression

name : NAME
integer : DEC_NUMBER
string : STRING

%import python (NAME, STRING, DEC_NUMBER)
%import common (WS)
%ignore WS
```
### Описание
- Все переменные глобальные
- Типы данных: uint, str
- Виды литералов:
  - Неотрицательные целочисленные: 123, 112358 (до 32 бит)
  - Строки: "abc", "qwerty"
- Поддержка математических операций (+, -, *, //, %)
- Код выполняется последовательно
- В стеке хранятся промежуточные аргументы и IP

## Организация памяти
- Гарвардская архитектура: память данных и команд разделены
- Машинное слова 32 бит
- Регистр команд - достаточно 40 бит (кодирование struct в json)

```
Регистры
+------------------------------------+
| ACC - аккумулятор                  |
+------------------------------------+
| CR - регистр инструкции            |
+------------------------------------+
| DR - регистр данных                |
+------------------------------------+
| IP - счётчик команд                |
+------------------------------------+
| SP - указатель стека               |
+------------------------------------+
| AR - адрес записи в память         |
+------------------------------------+

Instruction memory
+------------------------------+
| 00  : program start          |
|    ...                       |
| 10  : jmp n                  |
| 11  : je n+1                 |
|    ...                       |
| n   :                        |
|    ...                       |
+------------------------------+

Data memory
+------------------------------+
| 00  : constant 1             |
| 01  : constant 2             |
|    ...                       |
| l+0 : string ptr             |
|    ...                       |
| c+0 : variable 1             |
|    ...                       |
|                              |
|                              |
|                              |
|                              |
+------------------------------+
```

## Система команд

### Особенности процессора
- a

### Набор инструкций

| Opcode | arg          | Описание                               |
|--------|--------------|----------------------------------------|
| load   | addr/literal | data_mem[addr]/literal -> acc          |
| store  | addr         | acc -> data_mem[addr]                  |
| push   |              | acc -> stack[SP--]                     |
| pop    |              | stack[SP++] -> acc                     |
|        |              |                                        |
| add    | addr/literal | acc + data_mem[addr]/literal -> acc    |
| sub    | addr/literal | acc - data_mem[addr]/literal -> acc    |
| mul    | addr/literal | acc * data_mem[addr]/literal -> acc    |
| div    | addr/literal | acc // data_mem[addr]/literal -> acc   |
| mod    | addr/literal | acc % data_mem[addr]/literal -> acc    |
|        |              |                                        |
| cmp    | addr/literal | acc - data_mem[addr]/literal -> ZF, CF |
| jmp    | addr         | addr -> IP                             |
| je     | addr         | Z == 1 ? addr -> IP                    |
| ja     | addr         | C == 0 ? addr -> IP                    |
| jb     | addr         | C == 1 ? addr -> IP                    |


## Транслятор

Интерфейс CLI: `make translator ARGS="input_file output_file"`
В выходном файле содержится json с заполнением instruction_memory и data_memory

Реализация в модуле [translator](./src/translator)

Этапы трансляции:
1. Построение AST с помощью библиотеки [lark](https://github.com/lark-parser/lark) по eBNF
2. Трансляция - обход нод AST и преобразование в машинный код

## Модель процессора

## Тестирование

Реализованные программы:

1. [hello](./examples/hello.lisp): печать "Hello world!"
2. [cat](./examples/cat.lisp): программа cat, ввод -> вывод
3. [hello_user_name](./examples/hello_user_name.lisp): запросить у пользователя его имя, считать его, вывести на экран приветствие
4. [prob5](./examples/prob5.lisp): вычисление наименьшего положительного числа, делящегося на все числа от 1 до 20

Golden тесты реализованы в [golden](./golden), конфигурация в [golden_test.py](./tests/golden_test.py)

CI при помощи Github Action:

```yaml
name: Checks

on: [push, pull_request]

jobs:
  quality:
    name: Nothing has broken
    runs-on: ubuntu-latest

    steps:
      - name: Check out the code
        uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v3
        with:
          python-version: "3.11"

      - name: Install poetry
        run: python -m pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Lint with ruff
        run: make lint

      - name: Run tests and show coverage
        run: make coverage
```

Пример использования и журнал работы процессора на примере `hello_world`

- Код:
(print "Hello world!")

- Машинный код:
```

```

- Вывод программы:
Hello world!

- Журнал работы:
``` 

```

## Статистика

