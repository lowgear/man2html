from core.utility import as_

SYNTAX_CHARS = {'<': "&lt;",
                '>': "&gt;",
                '&': "&amp;", }
HTML_ESCAPES = {
    '\u2006': "&#x2006;",
    '\u2212': "&#x2212;",
}


@as_(''.join)
def escape(string: str):
    for char in string:
        # if char in SYNTAX_CHARS:
        #     yield SYNTAX_CHARS[char]
        if char in HTML_ESCAPES:
            yield HTML_ESCAPES[char]
        else:
            yield char
