import datetime

import dominate
from dominate import document
from dominate.tags import *

from core.args_parser import ArgsParser
from core.man_process_state import ManProcessState


def now():
    return datetime.datetime.now()


def alternate_map(first_func, second_func, sequence):
    count = 0
    for element in sequence:
        if count % 2 == 0:
            yield first_func(element)
        else:
            yield second_func(element)
        count += 1

def identical(x):
    return x


class Man2HtmlTranslator(object):
    def __init__(self, args_parser: ArgsParser):
        self.args_parser = args_parser
        self.commands = dict()

        self.apply_default_setting()

    def translate(self, lines):
        '''Принять строки разметки man и вернуть рузультат преобразования в
        html'''
        if lines is None:
            raise ValueError("lines should not be null")

        state = ManProcessState()
        nodes = []
        for line in lines:
            man_args = self.args_parser.parse_args(line)

            if len(man_args) == 0:
                nodes.append(p())
                continue

            if man_args[0] not in self.commands.keys():
                nodes.append(" ".join(man_args))
                continue

            man_command = self.commands.get(man_args[0])
            args = man_args[1:]

            man_command(state, nodes, *args)

        return self.compile_page(nodes, state)

    def handle_translation_mode(self, state: ManProcessState, nodes: list,
                                mode: str, *args):
        pass  # todo handle mode actually

    def compile_page(self, nodes: list, state: ManProcessState):
        doc = dominate.document()
        self.add_hat(doc, nodes, state)
        self.add_content(doc, nodes, state)
        self.add_footer(doc, nodes, state)

        return doc.render()

    def add_hat(self, doc: document, nodes: list, state: ManProcessState):
        doc.set_title("Man page for {}".format(state.title))
        doc.add("Section: {} ({})".format(state.manual, state.section),
                br(),
                "Source: {}".format(state.source),
                br(),
                "Updated: {}".format(state.date),
                hr())

    def add_content(self, doc: document, nodes: list, state: ManProcessState):
        if len(nodes) == 0:
            doc.add(p())
            return
        for node in nodes:
            if type(node) is str and not str.isalnum(node[0]):
                doc.add(node)
                continue
            doc.add('\n')
            doc.add(node)

    def add_footer(self, doc: document, nodes: list, state: ManProcessState):
        doc.add(hr())
        current_time = now()
        doc.add(current_time.strftime("Time: %H:%M:%S %Z, %B %d, %Y"))

    @staticmethod
    def handle_TH(state: ManProcessState, nodes: list, man_title: str= "",
                  man_section: str="", date: str="", man_source: str="",
                  manual: str=""):
        state.title = man_title
        state.section = man_section
        state.date = date
        state.source = man_source
        state.manual = manual

    @staticmethod
    def handle_SH(state: ManProcessState, nodes: list, *args):
        nodes.append(h2(" ".join(args)))

    @staticmethod
    def handle_SS(state: ManProcessState, nodes: list, *args):
        nodes.append(h3(" ".join(args)))

    @staticmethod
    def handle_comment(state: ManProcessState, nodes: list, *args):
        pass

    @staticmethod
    def handle_B(state: ManProcessState, nodes: list, *args):
        nodes.append(b(args))

    @staticmethod
    def handle_I(state: ManProcessState, nodes: list, *args):
        nodes.append(i(args))

    @staticmethod
    def handle_BR(state: ManProcessState, nodes: list, *args):
        nodes.extend(alternate_map(b, span, args))

    @staticmethod
    def handle_RB(state: ManProcessState, nodes: list, *args):
        nodes.extend(alternate_map(span, b, args))

    @staticmethod
    def handle_IR(state: ManProcessState, nodes: list, *args):
        nodes.extend(alternate_map(i, identical, args))

    @staticmethod
    def handle_RI(state: ManProcessState, nodes: list, *args):
        nodes.extend(alternate_map(span, i, args))

    @staticmethod
    def handle_page_char(state: ManProcessState, nodes: list, *args):
        pass  # todo actually handle it

    @staticmethod
    def handle_br(state: ManProcessState, nodes: list, *args):
        nodes.append(br())

    def apply_default_setting(self):
        self.commands[".\\\""] = self.handle_comment
        self.commands["'\\\""] = self.handle_translation_mode
        self.commands[".TH"] = self.handle_TH
        self.commands[".SH"] = self.handle_SH
        self.commands[".SS"] = self.handle_SS
        self.commands[".B"] = self.handle_B
        self.commands[".I"] = self.handle_I
        self.commands[".BR"] = self.handle_BR
        self.commands[".RB"] = self.handle_RB
        self.commands[".RI"] = self.handle_RI
        self.commands[".IR"] = self.handle_IR
        self.commands[".pc"] = self.handle_page_char
        self.commands[".br"] = self.handle_br
