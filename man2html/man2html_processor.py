import io


class Man2HtmlProcessor(object):
    def __init__(self):
        self.commands = dict()
        self.string_builder = []

    def consume(self, line: str):
        '''Принять очередную строку и добавить результат в место назначения'''
        if line is None:
            raise ValueError("line should not be null")

        man_args = self.__parse_man_args(line)

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

    @staticmethod
    def __parse_man_args(line: str):
    '''Парсит строку на аргументы Man pages.
    Двойные кавычки окружают текст, который нужно считать одним аргументом.
    Символ обратного слеша(\) экранирует действие двойных кавычек,
    разделяющее свойство пробельных символов'''
