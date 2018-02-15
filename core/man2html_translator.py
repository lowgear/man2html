import datetime
import math
import re
from functools import wraps, partial

import dominate
import dominate.tags as tags
from dominate import document

from core.args_parser import ArgsParser
from core.html_utils import escape
from core.man_process_state import ManProcessState, FILL_MODE_REGISTER
from core.settings import DEFAULT_SETTINGS, TranslationModes
from core.string_utils import expand_string, split_args
from core.utility import empty, first

dot_like_punctuation = ',.?!;:'
number_regex = re.compile(r"(\d+|\d+.\d*|\d*.\d+)")
comparision_regex = re.compile(
    '^' + number_regex.pattern + r"(=|<|>|<=|>=|!=|==)" +  # todo
    number_regex.pattern + '$')

CSS_RESET = r"""
dl, dt, dd, ol, ul, li,
{
    margin: 0;
    padding: 0;
    border: 0;
    vertical-align: baseline;
}
"""


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


def checks_for_word_break(func):
    # noinspection PyUnusedLocal
    @wraps(func)
    def wrapped(self, state, *args, **kwargs):
        if not empty(args) and args[0][0] not in dot_like_punctuation:
            state.paragraph.add(' ')
        return func(state, *args, **kwargs)

    return wrapped


def tag_from_raw_string(func):
    @wraps(func)
    def wrapped(*args, **__):
        tag = func()
        tag.add_raw_string(escape(" ".join(args)))
        return tag

    return wrapped


def escapes_args(func):
    @wraps(func)
    def wrapped(self, state: ManProcessState, *args, **kwargs):
        return func(self, state, *map(escape, args), **kwargs)

    return wrapped


# noinspection PyMethodMayBeStatic
class Man2HtmlTranslator(object):
    def __init__(self, args_parser: ArgsParser, strict_mode=True):
        self.args_parser = args_parser
        self.commands = dict()

        self.is_strict_mode = strict_mode

        self.apply_default_setting()

    def compile_page(self, state: ManProcessState):
        state.close_paragraph()
        doc = dominate.document()
        s = tags.style()
        s.add_raw_string(CSS_RESET)
        doc.head.appendChild(s)
        self.add_hat(doc, state)
        self.add_content(doc, state)
        self.add_footer(doc, state)

        return doc.render()

    def add_hat(self, doc: document, state: ManProcessState):
        doc.set_title("Man page for {}".format(state.title))
        doc.add("Section: {} ({})".format(state.manual, state.section),
                tags.br(),
                "Source: {}".format(state.source),
                tags.br(),
                "Updated: {}".format(state.date),
                tags.hr())

    def add_content(self, doc: document, state: ManProcessState):
        if len(state.nodes) == 0:
            doc.add(tags.p())
            return
        for node in state.nodes:
            if type(node) is str and not str.isalnum(node[0]):
                doc.add(node)
                continue
            doc.add('\n')
            doc.add(node)

    # noinspection PyUnusedLocal
    def add_footer(self, doc: document, state: ManProcessState):
        doc.add(tags.hr())
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

        state.relative_indents.clear()

    # noinspection PyPep8Naming
    def handle_SH(self, state: ManProcessState, *args, **__):
        """Заголовок."""
        state.nodes.append(tags.h2(" ".join(args)))

    # noinspection PyPep8Naming
    def handle_SS(self, state: ManProcessState, *args, **__):
        """Подзаголовок."""
        state.nodes.append(tags.h3(" ".join(args)))

    def handle_comment(self, state: ManProcessState, *_, **__):
        """Строка с комментарием."""
        pass

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_B(state: ManProcessState, *args, **__):
        """Bold."""
        return state.paragraph.add(tag_from_raw_string(tags.b)(*args))

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_I(state: ManProcessState, *args, **__):
        """Italic."""
        return state.paragraph.add(tag_from_raw_string(tags.i)(*args))

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_BR(state: ManProcessState, *args, **__):
        """Чередование Bold и Roman."""
        state.paragraph.add(alternate_map(tag_from_raw_string(tags.b),
                                          tag_from_raw_string(tags.span),
                                          args))

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_RB(state: ManProcessState, *args, **__):
        """Чередование Roman и Bold."""
        state.paragraph.add(alternate_map(tag_from_raw_string(tags.span),
                                          tag_from_raw_string(tags.b), args))

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_IR(state: ManProcessState, *args, **__):
        """Чередование Italic и Roman."""
        state.paragraph.add(alternate_map(tag_from_raw_string(tags.i),
                                          tag_from_raw_string(tags.span),
                                          args))

    # noinspection PyPep8Naming,PyMethodParameters
    @escapes_args
    @checks_for_word_break
    def handle_RI(state: ManProcessState, *args, **__):
        """Чередование Roman и Italic"""
        state.paragraph.add(alternate_map(tag_from_raw_string(tags.span),
                                          tag_from_raw_string(tags.i), args))

    def handle_page_char(self, state: ManProcessState, *args, **kwargs):
        pass  # todo actually handle it

    def handle_br(self, state: ManProcessState, *_, **__):
        """Перенос строки."""
        state.nodes.append(tags.br())

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

    def handle_if(self, state: ManProcessState, condition, *args, **__):
        """Условный оператор."""
        if self._calc_condition(state, condition):
            self.accept_line(state, args)

    # todo is indentation used once or saved for further use?
    # noinspection PyPep8Naming
    def handle_PP(self, state: ManProcessState, *_, **__):
        """Отступ перед первой строкой параграфа."""
        state.paragraph.attributes["style"] += ";text-indent:4em"  # todo
        state.prev_tagged_par_indent = state.get_default_indent()  # todo

    # noinspection PyPep8Naming
    def handle_TP(self, state: ManProcessState, indent=None, *_, **__):
        """Тегированный параграф."""
        indent = self.get_tagged_par_indent(indent, state)

        state.reset_paragraph()

        prev_nodes_num = len(state.nodes)
        while state.has_more_lines() and empty(state.paragraph):
            self.accept_line(state)
        tag = tags.dt()
        tag.attributes["style"] = state.paragraph.attributes["style"]
        for child in state.paragraph.children:
            tag.add_raw_string(child)
        state.reset_paragraph()

        tmp_ind = state.relative_indents
        state.relative_indents = [indent]
        state.paragraph.attributes["style"] = state.compile_style()
        state.relative_indents = tmp_ind

        while state.has_more_lines():
            arg = self.extract_command(state)
            if arg is not None and arg in self.commands.keys() and \
                    self.commands[arg].breaks:
                break
            self.accept_line(state)

        par = tags.dd(state.paragraph)
        state.reset_paragraph()

        if prev_nodes_num != 0 and \
                isinstance(state.nodes[prev_nodes_num - 1], tags.dl):
            element = state.nodes[prev_nodes_num - 1]
            element.add(tag)
            element.add(par)
        else:
            element = tags.dl()
            element.add(tag)
            element.add(par)
            state.nodes.insert(prev_nodes_num, element)

    def get_tagged_par_indent(self, indent, state):
        if indent is None:
            indent = state.prev_tagged_par_indent
        else:
            try:
                indent = int(indent)
            except ValueError:  # todo log
                indent = state.get_default_indent()  # todo
            state.prev_tagged_par_indent = indent
        return indent

    # noinspection PyPep8Naming
    def handle_IP(self, state: ManProcessState, tag: str = None,
                  indent: str = None, *_, **__):
        indent = self.get_tagged_par_indent(indent, state)
        if tag is None:
            tmp_ind = state.relative_indents
            state.relative_indents = [indent]
            state.paragraph.attributes["style"] = state.compile_style()
            state.relative_indents = tmp_ind
            return

        prev_nodes_num = len(state.nodes)

        t = tags.dt()
        t.add_raw_string(tag)
        tag = t

        tmp_ind = state.relative_indents
        state.relative_indents = [indent]
        state.paragraph.attributes["style"] = state.compile_style()
        state.relative_indents = tmp_ind

        while state.has_more_lines():
            arg = self.extract_command(state)
            if arg is not None and arg in self.commands.keys() and \
                    self.commands[arg].breaks:
                break
            self.accept_line(state)

        par = tags.dd(state.paragraph)
        state.reset_paragraph()

        if prev_nodes_num != 0 and \
                isinstance(state.nodes[prev_nodes_num - 1], tags.dl):
            element = state.nodes[prev_nodes_num - 1]
            element.add(tag)
            element.add(par)
        else:
            element = tags.dl()
            element.add(tag)
            element.add(par)
            state.nodes.insert(prev_nodes_num, element)

    def extract_command(self, state):
        cur_args = split_args(state.peek_line())
        return first(cur_args)

    # noinspection PyPep8Naming
    def handle_PD(self, state: ManProcessState, indent=None, *_, **__):
        """Отступ между параграфами."""
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
        """Строка на один пункт меньше."""
        pass  # todo

    def handle_nr(self, state: ManProcessState, register: str = None,
                  value: str = None,
                  auto_inc: str = None, *_, **__):
        if register is None or value is None:
            return  # todo log
        try:
            value = int(value)
        except ValueError:
            return  # todo log
        if auto_inc is not None:
            raise NotImplementedError()
            # noinspection PyUnreachableCode
            try:
                auto_inc = int(auto_inc)
            except ValueError:
                # auto_inc не является необходимым аргументом
                pass  # todo log or break on strict mode or something
        else:
            auto_inc = 0

        state.registers[register] = value
        # todo handle auto_inc

    def handle_sp(self, state: ManProcessState, value: str = None, *_, **__):
        if value is not None:
            try:
                value = int(math.ceil(float(value)))
            except ValueError:
                return  # todo log
        else:
            value = 1

        if not empty(state.paragraph.children) and not str(
                state.paragraph.children[-1]).endswith(str(tags.br())):
            state.paragraph.add(tags.br())
        for i in range(value):
            state.paragraph.add(tags.br())

    # noinspection PyPep8Naming
    def handle_RS(self, state: ManProcessState, value: str = None, *_, **__):
        if value is None:
            value = state.get_default_indent()
        else:
            try:
                value = float(value)
            except ValueError:
                value = state.get_default_indent()  # todo log

        state.relative_indents.append(value)

    # noinspection PyPep8Naming
    def handle_RE(self, state: ManProcessState, value: str = None, *_, **__):
        if value is None:
            state.relative_indents.pop()
        else:
            raise NotImplementedError()  # todo

    def handle_nf(self, state: ManProcessState, *_, **__):
        # todo
        # state.nodes.append(tags.br())
        state.registers[FILL_MODE_REGISTER] = 0
        state.close_paragraph()

    def handle_fi(self, state: ManProcessState, *_, **__):
        # todo
        # state.nodes.append(tags.br())
        state.registers[FILL_MODE_REGISTER] = 1
        state.close_paragraph()

    def handle_ie(self, state: ManProcessState, condition: str, *args, **__):
        if self._calc_condition(state, condition):
            self.accept_line(state, args)
        else:
        pass  # todo

    def apply_default_setting(self):
        self.commands[".\\\""] = Command(self.handle_comment, False)
        self.commands["'\\\""] = Command(self.handle_translation_mode, False)
        self.commands[".TH"] = Command(self.handle_TH, False)
        self.commands[".SH"] = Command(self.handle_SH, True, True)
        self.commands[".SS"] = Command(self.handle_SS, True)
        self.commands[".B"] = Command(self.handle_B, False)
        self.commands[".I"] = Command(self.handle_I, False)
        self.commands[".FN"] = Command(self.handle_I, False)  # todo alias?
        self.commands[".BR"] = Command(self.handle_BR, False)
        self.commands[".RB"] = Command(self.handle_RB, False)
        self.commands[".RI"] = Command(self.handle_RI, False)
        self.commands[".IR"] = Command(self.handle_IR, False)
        self.commands[".pc"] = Command(self.handle_page_char, False)
        self.commands[".br"] = Command(self.handle_br, True)
        self.commands[".de"] = Command(self.handle_de, False)
        self.commands[".if"] = Command(self.handle_if, False)
        self.commands[".PP"] = Command(self.handle_PP, True, True)
        # LP is alias of PP
        self.commands[".LP"] = Command(self.handle_PP, True, True)
        self.commands[".TP"] = Command(self.handle_TP, True)
        self.commands[".PD"] = Command(self.handle_PD, False)
        self.commands[".SM"] = Command(self.handle_SM, False)
        self.commands[".nr"] = Command(self.handle_nr, False)
        self.commands[".sp"] = Command(self.handle_sp, False)
        self.commands[".RS"] = Command(self.handle_RS, True, True)
        self.commands[".RE"] = Command(self.handle_RE, True, True)
        self.commands[".IP"] = Command(self.handle_IP, True)
        self.commands[".nf"] = Command(self.handle_nf, False)
        self.commands[".fi"] = Command(self.handle_fi, False)
        self.commands[".ie"] = Command(self.handle_ie, False)

    def register_macros(self, macros_name: str, macros_lines: list):
        pass  # todo actually register macros

    def accept_line(self, state: ManProcessState, args: tuple = None):
        if state.registers.get(FILL_MODE_REGISTER) == 0:
            state.break_line()
        if args is None:
            line_builder = []
            while empty(line_builder) or line_builder[-1].endswith("\\\n"):
                if not empty(line_builder):
                    line_builder[-1] = line_builder[-1][:-2]
                line_builder.append(state.pop_line())
            line = "".join(line_builder)
            args = split_args(line)
            args = tuple(map(partial(expand_string, state), args))

        if empty(args):
            state.close_paragraph()
            return

        if args[0] not in self.commands.keys():
            if args[0][0] == '.':
                import sys
                print(' '.join(args), file=sys.stderr)
            if args[0][0] == '.' and self.is_strict_mode:
                raise NotImplementedError(' '.join(args))
            if state.registers.get(FILL_MODE_REGISTER) == 0:
                state.add_to_paragraph(expand_string(state, line))  # todo
                # blyat'
                return
            self.default_handle(state, *args)
            return

        man_command = self.commands.get(args[0])
        args = args[1:]

        if man_command.breaks:
            state.close_paragraph()
        man_command.action(state, *args)

    # noinspection PyMethodParameters
    @checks_for_word_break
    def default_handle(state: ManProcessState, *args):
        state.add_to_paragraph(" ".join(args))

    def _calc_condition(self, state: ManProcessState, condition: str):
        if condition[0] == '!':
            return not self._calc_condition(state, condition[1:])
        if condition == "n":
            return state.translation_mode == TranslationModes.NROFF
        if condition == "t":
            return state.translation_mode == TranslationModes.TROFF
        if condition[0] == 'r':
            return condition[1:] in state.registers.keys()
        match = comparision_regex.match(condition)
        if match is not None:
            if match.group(2) == '=':
                condition = condition.replace('=', '==')
            return eval(condition)

        return False
        # raise NotImplementedError()  # todo


class Command:
    def __init__(self, action, breaks: bool, resets: bool = False):
        self.action = action
        self.breaks = breaks
        self.resets = resets
