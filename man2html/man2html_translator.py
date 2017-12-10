import datetime

import dominate
from dominate import document
from dominate.tags import *

from args_parser import ArgsParser
from man_process_state import ManProcessState


def now():
    return datetime.datetime.now()


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
                continue

            if man_args[0] not in self.commands.keys():
                nodes.extend(man_args)
                continue

            man_command = self.commands.get(man_args[0])
            args = man_args[1:]

            man_command(state, nodes, *args)

        return self.compile_page(nodes, state)

    def apply_default_setting(self):
        self.commands[".TH"] = self.handle_th
        self.commands[".SH"] = self.handle_sh

    @staticmethod
    def handle_th(state: ManProcessState, nodes: list, man_title: str="",
                  man_section: str="", date: str="", man_source: str="",
                  manual: str=""):
        state.title = man_title
        state.section = man_section
        state.date = date
        state.source = man_source
        state.manual = manual

    @staticmethod
    def handle_sh(state: ManProcessState, nodes: list, name: str="", *args):
        nodes.append(h2(name))
        nodes.extend(args)

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
        doc.add(nodes)

    def add_footer(self, doc: document, nodes: list, state: ManProcessState):
        doc.add(hr())
        current_time = now()
        doc.add(current_time.strftime("Time: %H:%M:%S %Z, %B %d, %Y"))
