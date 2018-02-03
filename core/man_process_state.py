from dominate.tags import p

from core.settings import DEFAULT_SETTINGS, TranslationModes
from core.utility import empty

before_margin_property = "-webkit-margin-before"
after_margin_property = "-webkit-margin-after"


class ManProcessState(object):
    def __init__(self, lines):
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
        self.reset_paragraph()
        self.registers = dict()

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
            before_margin_property + ":" +
            str(self.inter_paragraph_indent) + "em",
            after_margin_property + ":" +
            str(self.inter_paragraph_indent) + "em",
        ])
