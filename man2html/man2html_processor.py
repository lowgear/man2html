from args_parser import ArgsParser


class Man2HtmlProcessor(object):
    def __init__(self, args_parser: ArgsParser):
        self.args_parser = args_parser
        self.commands = dict()
        self.string_builder = []

    def consume(self, line: str):
        '''Принять очередную строку и добавить результат в место назначения'''
        if line is None:
            raise ValueError("line should not be null")

        man_args = self.args_parser.parse_args(line)

        if len(man_args) == 0:
            return

        if man_args[0] not in self.commands.keys():
            self.string_builder.extend(man_args)
            return

        command = self.commands.get(man_args[0])
        args = man_args[1:]

        self.string_builder.extend(command(*args))

    def translate(self):
        pass
