import re

from core.args_parser import ESCAPE_CHAR
from core.man_process_state import ManProcessState
from core.utility import as_

COMMENT_CHAR = '"'
DOUBLE_QUOTE = '"'

macros = []


def registered_macro(regex: str):
    def decorator(macro):
        macros.append((re.compile(regex), macro))
        return macro

    return decorator


@registered_macro(r"\\e")
def backslash(_: ManProcessState, builder: list, __):
    builder.append("\\")


@registered_macro(r"\\-")
def minus_sign(_: ManProcessState, builder: list, __):
    builder.append("\u2212")


@registered_macro(r"\\\|")
def non_breaking_space(_: ManProcessState, builder: list, __):
    builder.append("\u2006")


@registered_macro(r"\\ ")
def space(_: ManProcessState, builder: list, __):
    builder.append(" ")


@registered_macro(r"\\c")
def backslash(_: ManProcessState, __: list, ___):
    pass  # todo actually do what?


@registered_macro(r"\\n([a-zA-Z.])")
def register_expansion(state: ManProcessState, builder: list, match):
    register_name = match.group(1)
    if register_name in state.registers.keys():
        builder.append(state.registers[register_name])


@registered_macro(r"\\n\(([a-zA-Z.]{2})")
def register_expansion_2(state: ManProcessState, builder: list, match):
    register_name = match.group(1).strip('.')
    if register_name in state.registers.keys():
        builder.append(state.registers[register_name])


@registered_macro(r"\\f([BIPR])")
def inline_set_font(state: ManProcessState, builder: list, match):
    font_name = match.group(1).strip('.')
    state.set_current_font(font_name)


@as_(tuple)
def expand_string(state: ManProcessState, line: str):
    line = ''.join(filter(lambda c: c != '\r' and c != '\n', line))

    arg_builder = []
    escaped = False
    double_quoted = False
    can_open_quotes = True
    arg_count = 0

    i = -1
    while i + 1 < len(line):
        i += 1
        char = line[i]

        macro_applied = False
        for reg, macro in macros:
            match = reg.match(line, i)
            if not match:
                continue
            macro_applied = True
            i += match.end() - match.start() - 1
            macro(state, arg_builder, match)

        if macro_applied:
            continue

        if escaped:
            escaped = False

            # макрос комментирования .\" и комментирование \" работают
            # по-разному
            if char == COMMENT_CHAR and not (arg_count == 0 and
                                             len(arg_builder) == 1 and
                                             arg_builder[0] == '.'):
                break

            arg_builder.append(ESCAPE_CHAR + char)
            continue

        if char == ESCAPE_CHAR:
            escaped = True
            continue

        if char == DOUBLE_QUOTE:
            if double_quoted:
                yield ''.join(arg_builder)
                arg_count += 1
                arg_builder.clear()
                double_quoted = False
                continue
            if can_open_quotes:
                double_quoted = True
                continue
            arg_builder.append(char)
            continue

        if not double_quoted and char.isspace():
            if len(arg_builder):
                yield ''.join(arg_builder)
                arg_count += 1
                arg_builder.clear()
            can_open_quotes = True
            continue

        arg_builder.append(char)
        can_open_quotes = False

    if double_quoted:
        arg_builder = [DOUBLE_QUOTE] + arg_builder

    if len(arg_builder):
        yield ''.join(arg_builder)
        arg_count += 1
        arg_builder.clear()
