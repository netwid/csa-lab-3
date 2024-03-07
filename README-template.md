# Лабораторная работа №3. Транслятор и модель процессора

- P33111. Кузьмин Илья Дмитриевич
- lisp | acc | harv | hw | instr | struct | stream | port | pstr | prob5 | 8bit (Базовый вариант)
- без усложнения

## Язык программирования
За основу языка взят диалект Common Lisp

### Syntax
```
include(src/translator/grammar.lark)
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
|    ... halt                  |
+------------------------------+

Data memory
+------------------------------+
| 00  : temp for ops           |
| 01  : vars                   |
|    ...                       |
| l+0 : const strings          |
|    ...                       |
| c+0 : dynamic data           |
|    ...                       |
|------------------------------|
| stack                        |
+------------------------------+
```

## Система команд

### Особенности процессора
- Машинное слово 32 бита, беззнаковое
- Поток управления:
  - Инкремент IP после каждой инструкции
  - Условные и безусловные переходы
- Адресация любого обращения в память абсолютная, поддержка литералов в командах

### Набор инструкций

| Opcode | arg          | Описание                               |
|--------|--------------|----------------------------------------|
| load   | addr/literal | data_mem[addr]/literal -> acc          |
| store  | addr         | acc -> data_mem[addr]                  |
| push   |              | acc -> stack[SP--]                     |
| pop    |              | SP++                                   |
| call   | addr         | stack[SP--] <- IP                      |
| ret    | addr         | stack[SP--] <- IP                      |
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
| jne    | addr         | Z == 0 ? addr -> IP                    |
| jb     | addr         | C == 1 ? addr -> IP                    |
| ja     | addr         | C == 0 && Z == 0 ? addr -> IP          |

## Транслятор

Интерфейс CLI: `make translator ARGS="input_file output_file"`
В выходном файле содержится json с заполнением instruction_memory и data_memory

Реализация в модуле [translator](./src/translator)

Этапы трансляции:
1. Построение AST с помощью библиотеки [lark](https://github.com/lark-parser/lark) по eBNF
2. Трансляция - обход нод AST и преобразование в машинный код
3. Повторный проход по командам и линковка переменных/строк после их размещения в памяти

## Модель процессора

Интерфейс CLI: `make machine ARGS="code_data_file input_file"`

Реализация в модуле [machine](./src/machine)

Datapath:


Control Unit:


## Тестирование

Реализованные программы:

1. [hello](./examples/hello.lisp): печать "Hello world!"
2. [cat](./examples/cat.lisp): программа cat, ввод -> вывод
3. [hello_user_name](./examples/hello_user_name.lisp): запросить у пользователя его имя, считать его, вывести на экран приветствие
4. [prob5](./examples/prob5.lisp): вычисление наименьшего положительного числа, делящегося на все числа от 1 до 20

Golden тесты реализованы в [golden](./golden), конфигурация в [golden_test.py](./tests/golden_test.py)

CI при помощи Github Action:

```yaml
include(.github/workflows/ci.yaml)
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

