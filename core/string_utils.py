import re

from core.args_parser import ESCAPE_CHAR
from core.man_process_state import ManProcessState
from core.utility import as_

COMMENT_CHAR = '"'
DOUBLE_QUOTE = '"'
SYNTAX_CHARS = {'<': "&lt;",
                '>': "&gt;",
                '&': "&amp;", }
HTML_ESCAPES = {
            '\u2006': "&#x2006;",
            '\u2212': "&#x2212;",
        }

macros = []


def registered_macro(regex: str):
    def decorator(macro):
        macros.append((re.compile(regex), macro))
        return macro

    return decorator


@registered_macro(r"\\e")
def backslash(_: ManProcessState, __):
    return "\\"


@registered_macro(r"\\-")
def minus_sign(_: ManProcessState, __):
    return "&#x2212;"


@registered_macro(r"\\\|")
def non_breaking_space(_: ManProcessState, __):
    return "&#x2006;"


@registered_macro(r"\\ ")
def space(_: ManProcessState, __):
    return " "


@registered_macro(r"\\\(co")
def copyright(_: ManProcessState, __):
    return "&#x00A9;"


@registered_macro(r"\\c")
def continue_(_: ManProcessState, __):
    pass  # todo actually do what?


@registered_macro(r"\\n([a-zA-Z.])")
def register_expansion(state: ManProcessState, match):
    register_name = match.group(1)
    if register_name in state.registers.keys():
        res = state.registers[register_name]
        if not isinstance(res, str):
            res = str(res)
        return res


@registered_macro(r"\\n\(([a-zA-Z.]{2})")
def register_expansion_2(state: ManProcessState, match):
    register_name = match.group(1).strip('.')
    if register_name in state.registers.keys():
        res = state.registers[register_name]
        if not isinstance(res, str):
            res = str(res)
        return res


font_modifiers = {"R": None,
                  "P": None,
                  "B": "b",
                  "I": "i",
                  "CW": "code"}


@registered_macro(r"\\f([BIPR])")
@as_("".join)
def inline_set_font(_: ManProcessState, match):
    font = match.group(1).strip('.')
    for tag in font_modifiers.values():
        if tag is not None:
            yield "</" + tag + ">"
    if font in font_modifiers.keys() and font_modifiers[font] is not None:
        yield "<" + font_modifiers[font] + ">"
    else:
        pass  # todo log
    # if font == "R" or font == "P":
    #     return "</b></i>"
    # elif font == "B":
    #     return "<b></i>"
    # elif font == "I":
    #     return "</b><i>"
    # else:
    #     return "</b></i>"  # todo log


@registered_macro(r"\\f\(([A-Za-z.]{2})")
@as_("".join)
def inline_set_font(_: ManProcessState, match):
    font = match.group(1).strip('.')
    for tag in font_modifiers.values():
        if tag is not None:
            yield "</" + tag + ">"
    if font in font_modifiers.keys() and font_modifiers[font] is not None:
        yield "<" + font_modifiers[font] + ">"
    else:
        pass  # todo log


@as_("".join)
def expand_string(state: ManProcessState, line: str):
    line = ''.join(filter(lambda c: c != '\r' and c != '\n', line))

    i = -1
    while i + 1 < len(line):
        i += 1
        char = line[i]

        macro_used = False
        for reg, macro in macros:
            match = reg.match(line, i)
            if match is None:
                continue
            macro_used = True
            i += match.end() - match.start() - 1
            char = macro(state, match)
            break

        if macro_used:
            if char is not None:
                yield char
            continue

        if char in SYNTAX_CHARS:
            yield SYNTAX_CHARS[char]
        elif char in HTML_ESCAPES:
            yield HTML_ESCAPES[char]
        else:
            yield char


@as_(tuple)
def split_args(string: str):
    string = ''.join(filter(lambda c: c != '\r' and c != '\n', string))

    arg_builder = []
    escaped = False
    double_quoted = False
    can_open_quotes = True
    arg_count = 0

    for char in string:
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

    if len(arg_builder):
        yield ''.join(arg_builder)
        arg_count += 1
        arg_builder.clear()