import dominate.tags as tags

from core.settings import DEFAULT_SETTINGS, TranslationModes
from core.utility import empty

before_margin = "-webkit-margin-before"
after_margin = "-webkit-margin-after"
margin_left = "margin-left"
text_indent = "text-indent"

FILL_MODE_REGISTER = '.u'


class ManProcessState(object):
    def __init__(self, lines):
        self.font = "R"
        self.title = ""
        self.section = ""
        self.date = ""
        self.source = ""
        self.manual = ""
        self.translation_mode = TranslationModes.NROFF
        self.index = 0
        self.lines = lines if isinstance(lines, list) else list(lines)
        self.nodes = list()
        self.inter_paragraph_indent = DEFAULT_SETTINGS[
            self.translation_mode].inter_paragraph_indent
        self.registers = dict()
        self.relative_indents = []
        self.prev_tagged_par_indent = 5  # todo nroff?

        self._init_registers()

        self.reset_paragraph()

    def has_more_lines(self):
        return self.index < len(self.lines)

    def pop_line(self):
        self.index += 1
        return self.lines[self.index - 1]

    def peek_line(self):
        return self.lines[self.index]

    def cur_paragraph_empty(self):
        return empty(self.paragraph)

    def close_paragraph(self):
        if not self.cur_paragraph_empty():
            self.nodes.append(self.paragraph)
        self.reset_paragraph()

    def reset_paragraph(self):
        # noinspection PyAttributeOutsideInit
        self.paragraph = self._new_paragraph()
        self.paragraph.attributes["style"] = self.compile_style()

    def compile_style(self):
        return ";".join([
            before_margin + ":" + str(self.inter_paragraph_indent) + "em",
            after_margin + ":" + str(self.inter_paragraph_indent) + "em",
            margin_left + ":" + "{:.1f}".format(sum(self.relative_indents)) +
            "em",
            text_indent + ":" + "0" + "em",
        ])

    def set_current_font(self, font_name):
        self.font = font_name

    def add_to_paragraph(self, string: str):
        self.paragraph.add_raw_string(string)  # todo log

    def get_default_indent(self):
        return 5 if self.translation_mode == TranslationModes.NROFF else 7.2

    def break_line(self):
        if empty(self.paragraph) or \
                isinstance(self.paragraph.children[-1], tags.br) or \
                str(self.paragraph.children[-1]).endswith("<br>"):
            return
        self.paragraph.add(tags.br())

    def _new_paragraph(self):
        if self.registers.get(FILL_MODE_REGISTER) == 1:
            return tags.p()
        return tags.pre()

    def _init_registers(self):
        self.registers[FILL_MODE_REGISTER] = 1
