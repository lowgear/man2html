from dominate.tags import p, b, i

from core.settings import DEFAULT_SETTINGS, TranslationModes
from core.utility import empty

before_margin = "-webkit-margin-before"
after_margin = "-webkit-margin-after"
margin_left = "margin-left"


class ManProcessState(object):
    def __init__(self, lines):
        self.font = "R"
        self.title = ""
        self.section = ""
        self.date = ""
        self.source = ""
        self.manual = ""
        self.translation_mode = TranslationModes.TROFF
        self.index = 0
        self.lines = lines if isinstance(lines, list) else list(lines)
        self.nodes = list()
        self.inter_paragraph_indent = DEFAULT_SETTINGS[
            self.translation_mode].inter_paragraph_indent
        self.registers = dict()
        self.relative_indents = []

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
        if self.cur_paragraph_empty():
            return
        self.nodes.append(self.paragraph)
        self.reset_paragraph()

    def reset_paragraph(self):
        # noinspection PyAttributeOutsideInit
        self.paragraph = p()
        self.paragraph.attributes["style"] = ";".join([
            before_margin + ":" + str(self.inter_paragraph_indent) + "v",
            after_margin + ":" + str(self.inter_paragraph_indent) + "v",
            margin_left + ":" + "{:.1f}".format(sum(self.relative_indents)) +
            "en",
        ])

    def set_current_font(self, font_name):
        self.font = font_name

    def add_to_paragraph(self, string: str):
        self.paragraph.add_raw_string(string)  # todo log
