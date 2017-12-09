class ArgsParser(object):
    def __init__(self):
        self.ESCAPE_CHAR = '\\'
        self.DOUBLE_QUOTE = '"'

        self.ESCAPED_MEANING = {
            'e': '\\'
        }

    def parse_args(self, line: str):
        '''Парсит строку на аргументы Man pages. Двойные кавычки,
        первая из которых должна быть либо первым символом строки,
        либо следовать за пробельным символом, окружают
        текст, который нужно считать одним аргументом. Символ обратного
        слеша(\) экранирует действие двойных кавычек, разделяющее свойство
        пробельных символов'''
        args = []
        current_arg_builder = []
        escaped = False
        double_quoted = False
        can_open_quotes = True
        for char in line:
            if escaped:
                if char in self.ESCAPED_MEANING.keys():
                    current_arg_builder.append(self.ESCAPED_MEANING[char])
                    continue
                current_arg_builder.append(self.ESCAPE_CHAR)

            if char == self.ESCAPE_CHAR:
                escaped = True
                continue

            if char == self.DOUBLE_QUOTE:
                if double_quoted:
                    args.append(''.join(current_arg_builder))
                    current_arg_builder.clear()
                    double_quoted = False
                    continue
                if can_open_quotes:
                    double_quoted = True
                    continue
                current_arg_builder.append(char)
                continue

            if not double_quoted and char.isspace():
                if len(current_arg_builder):
                    args.append(''.join(current_arg_builder))
                    current_arg_builder.clear()
                can_open_quotes = True
                continue

            current_arg_builder.append(char)
            can_open_quotes = False

        if double_quoted:
            current_arg_builder = [self.DOUBLE_QUOTE] + current_arg_builder

        if len(current_arg_builder):
            args.append(''.join(current_arg_builder))
            current_arg_builder.clear()

        return args
