import datetime

import dominate
from dominate import document
from dominate.tags import *

from core.args_parser import ArgsParser
from core.man_process_state import ManProcessState
from core.settings import DEFAULT_SETTINGS, TranslationModes
from core.utility import empty, first

dot_like_punctuation = ',.?!;:'


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


def checks_for_word_break(func):
    def result(self, state, *args, **kwargs):
        if not empty(args) and args[0][0] not in dot_like_punctuation:
            state.paragraph.add(' ')
        return func(self, state, *args, **kwargs)

    return result


# noinspection PyMethodMayBeStatic
class Man2HtmlTranslator(object):
    def __init__(self, args_parser: ArgsParser, strict_mode=True):
        self.args_parser = args_parser
        self.commands = dict()

        self.strict_mode = strict_mode

        self.apply_default_setting()

    def compile_page(self, state: ManProcessState):
        state.close_paragraph()
        doc = dominate.document()
        self.add_hat(doc, state)
        self.add_content(doc, state)
        self.add_footer(doc, state)

        return doc.render()

    def add_hat(self, doc: document, state: ManProcessState):
        doc.set_title("Man page for {}".format(state.title))
        doc.add("Section: {} ({})".format(state.manual, state.section),
                br(),
                "Source: {}".format(state.source),
                br(),
                "Updated: {}".format(state.date),
                hr())

    def add_content(self, doc: document, state: ManProcessState):
        if len(state.nodes) == 0:
            doc.add(p())
            return
        for node in state.nodes:
            if type(node) is str and not str.isalnum(node[0]):
                doc.add(node)
                continue
            doc.add('\n')
            doc.add(node)

    # noinspection PyUnusedLocal
    def add_footer(self, doc: document, state: ManProcessState):
        doc.add(hr())
        current_time = now()
        doc.add(current_time.strftime("Time: %H:%M:%S %Z, %B %d, %Y"))

    def translate(self, lines):
        """Принять строки разметки man и вернуть рузультат преобразования в
        html"""
        if lines is None:
            raise ValueError("lines should not be null")

        state = ManProcessState(lines)
        while state.has_more_lines():
            self.accept_line(state)

        return self.compile_page(state)

    def handle_translation_mode(self, state: ManProcessState, mode: str, *_,
                                **__):
        if mode == "n":
            state.translation_mode = TranslationModes.NROFF
        elif mode == "t":
            state.translation_mode = TranslationModes.TROFF

    # noinspection PyPep8Naming
    def handle_TH(self, state: ManProcessState, man_title: str = "",
                  man_section: str = "", date: str = "", man_source: str = "",
                  manual: str = "", *_, **__):
        """Описание страницы Man."""
        state.title = man_title
        state.section = man_section
        state.date = date
        state.source = man_source
        state.manual = manual

    # noinspection PyPep8Naming
    def handle_SH(self, state: ManProcessState, *args, **__):
        """Заголовок."""
        state.nodes.append(h2(" ".join(args)))

    # noinspection PyPep8Naming
    def handle_SS(self, state: ManProcessState, *args, **__):
        """Подзаголовок."""
        state.nodes.append(h3(" ".join(args)))

    def handle_comment(self, state: ManProcessState, *_, **__):
        """Строка с комментарием."""
        pass

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_B(self, state: ManProcessState, *args, **__):
        """Bold."""
        state.paragraph.add(b(args))

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_I(self, state: ManProcessState, *args, **__):
        """Italic."""
        state.paragraph.add(i(args))

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_BR(self, state: ManProcessState, *args, **__):
        """Чередование Bold и Roman."""
        state.paragraph.add(alternate_map(b, span, args))

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_RB(self, state: ManProcessState, *args, **__):
        """Чередование Roman и Bold."""
        state.paragraph.add(alternate_map(span, b, args))

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_IR(self, state: ManProcessState, *args, **__):
        """Чередование Italic и Roman."""
        state.paragraph.add(alternate_map(i, identical, args))

    # noinspection PyPep8Naming
    @checks_for_word_break
    def handle_RI(self, state: ManProcessState, *args, **__):
        """Чередование Roman и Italic"""
        state.paragraph.add(alternate_map(span, i, args))

    def handle_page_char(self, state: ManProcessState, *args, **kwargs):
        pass  # todo actually handle it

    def handle_br(self, state: ManProcessState, *_, **__):
        """Перенос строки."""
        state.nodes.append(br())

    def handle_de(self, state: ManProcessState, *args, **__):
        """Определение макроса"""
        if len(args) == 0:
            return
        stop = ".."
        if len(args) > 1:
            stop = "." + args[1]
        stop_index = state.index
        while str.strip(state.lines[stop_index]) != stop:
            stop_index += 1
        macros_lines = state.lines[state.index:stop_index]
        self.register_macros(args[0], macros_lines)

        state.index = stop_index + 1

    def handle_if(self, state: ManProcessState, condition, *args,
                  **__):
        """Условный оператор."""
        if condition == "n":
            if state.translation_mode == TranslationModes.NROFF:
                self.accept_line(state, *args)
        elif condition == "t":
            if state.translation_mode == TranslationModes.TROFF:
                self.accept_line(state, *args)
        else:
            pass
            # raise NotImplementedError()  # todo

    # noinspection PyPep8Naming
    def handle_PP(self, state: ManProcessState, *_, **__):
        """Отступ перед первой строкой параграфа."""
        state.paragraph.attributes["style"] += ";text-indent:4em"

    # noinspection PyPep8Naming
    def handle_TP(self, state: ManProcessState, indent=None, *_, **__):
        """Тегированный параграф."""
        if indent is None:
            indent = 5
        else:
            try:
                indent = int(indent)
            except ValueError:  # todo log
                indent = 5

        prev_nodes_num = len(state.nodes)
        while state.has_more_lines() and empty(state.paragraph):
            self.accept_line(state)
        tag = dt(list(state.paragraph))
        state.reset_paragraph()

        while state.has_more_lines():
            cur_args = self.args_parser.parse_args(state.peek_line())
            arg = first(cur_args)
            if arg is not None and arg in self.commands.keys() and \
                    self.commands[arg].breaks:
                break
            self.accept_line(state)
        par = dd(state.paragraph)
        state.reset_paragraph()

        par.attributes["text-indent"] = str(indent) + "en"
        if prev_nodes_num != 0 and \
                isinstance(state.nodes[prev_nodes_num - 1], dl):
            element = state.nodes[prev_nodes_num - 1]
            element.add(tag)
            element.add(par)
        else:
            element = dl()
            element.add(tag)
            element.add(par)
            state.nodes.insert(prev_nodes_num, element)

    # noinspection PyPep8Naming
    def handle_PD(self, state: ManProcessState, indent=None, *_, **__):
        """Отступ перед первой строкой параграфа."""
        if indent is None:
            indent = \
                DEFAULT_SETTINGS[state.translation_mode].inter_paragraph_indent
        else:
            try:
                indent = float(indent)
            except ValueError:  # todo log
                state.inter_paragraph_indent = \
                    DEFAULT_SETTINGS[
                        state.translation_mode].inter_paragraph_indent
        state.inter_paragraph_indent = indent

    # noinspection PyPep8Naming
    def handle_SM(self, state: ManProcessState, text="", *_, **__):
        """Отступ перед первой строкой параграфа."""
        pass  # todo

    def apply_default_setting(self):
        self.commands[".\\\""] = Command(self.handle_comment, False)
        self.commands["'\\\""] = Command(self.handle_translation_mode, False)
        self.commands[".TH"] = Command(self.handle_TH, False)
        self.commands[".SH"] = Command(self.handle_SH, True, True)
        self.commands[".SS"] = Command(self.handle_SS, True)
        self.commands[".B"] = Command(self.handle_B, False)
        self.commands[".I"] = Command(self.handle_I, False)
        self.commands[".BR"] = Command(self.handle_BR, False)
        self.commands[".RB"] = Command(self.handle_RB, False)
        self.commands[".RI"] = Command(self.handle_RI, False)
        self.commands[".IR"] = Command(self.handle_IR, False)
        self.commands[".pc"] = Command(self.handle_page_char, False)
        self.commands[".br"] = Command(self.handle_br, True)
        self.commands[".de"] = Command(self.handle_de, False)
        self.commands[".if"] = Command(self.handle_if, False)
        self.commands[".PP"] = Command(self.handle_PP, True, True)
        self.commands[".TP"] = Command(self.handle_TP, True)
        self.commands[".PD"] = Command(self.handle_PD, False)
        self.commands[".SM"] = Command(self.handle_SM, False)

    def register_macros(self, macros_name: str, macros_lines: list):
        pass  # todo actually register macros

    def accept_line(self, state: ManProcessState, *args):
        if empty(args):
            line = state.pop_line()
            args = list(self.args_parser.parse_args(line))

        if len(args) == 0:
            state.close_paragraph()
            return

        if args[0] not in self.commands.keys():
            if args[0][0] == '.':
                import sys
                print(' '.join(args), file=sys.stderr)
            if args[0][0] == '.' and self.strict_mode:
                raise NotImplementedError(' '.join(args))
            self.default_handle(state, *args)
            return

        man_command = self.commands.get(args[0])
        args = args[1:]

        if man_command.breaks:
            state.close_paragraph()
        man_command.action(state, *args)

    @checks_for_word_break
    def default_handle(self, state, *args):
        state.paragraph.add(" ".join(args))


class Command:
    def __init__(self, action, breaks: bool, resets: bool = False):
        self.action = action
        self.breaks = breaks
        self.resets = resets
