from enum import Enum, auto


class Setting():
    def __init__(self, inter_paragraph_indent):
        self.inter_paragraph_indent = inter_paragraph_indent


class TranslationModes(Enum):
    TROFF = auto()
    NROFF = auto()


DEFAULT_SETTINGS = {
    TranslationModes.TROFF: Setting(0.4),
    TranslationModes.NROFF: Setting(1)
}
