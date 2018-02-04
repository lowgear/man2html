from core.args_parser import ESCAPE_CHAR
from core.man_process_state import ManProcessState


expansions = dict()
SYNTAX_CHARS = {'<': "&lt;",
                '>': "&gt;",
                '&': "&amp;", }
ESCAPED_MEANING = {
            'e': '\\',
            '|': "&#x2006",  # "\u2006",
            '-': "&#x2212",
            ' ': " ",
            'c': ""
        }


def expand_arg(state: ManProcessState, arg: str):
    builder = []
    escaped = False
    for char in arg:
        if escaped:
            escaped = False
            if char in ESCAPED_MEANING.keys():
                builder.append(ESCAPED_MEANING[char])
                continue

            builder.append(ESCAPE_CHAR + char)
            continue

        if char == ESCAPE_CHAR:
            escaped = True
            continue

        if char in SYNTAX_CHARS.keys():
            char = SYNTAX_CHARS[char]
        builder.append(char)
    return ''.join(builder)
