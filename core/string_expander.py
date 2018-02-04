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
            # if char in self.ESCAPED_MEANING.keys():
            #     current_arg_builder.append(self.ESCAPED_MEANING[char])
            #     continue
            # current_arg_builder.append(self.ESCAPE_CHAR)
            builder.append(ESCAPE_CHAR + char)
            continue

        if char == ESCAPE_CHAR:
            escaped = True
            continue

        if char in SYNTAX_CHARS.keys():
            char = SYNTAX_CHARS[char]
        builder.append(char)
    return ''.join(builder)
