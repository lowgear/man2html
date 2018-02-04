from core.args_parser import ESCAPE_CHAR
from core.man_process_state import ManProcessState


class StringExpander:
    expansions = dict()

    @staticmethod
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
            builder.append(char)
        return ''.join(builder)