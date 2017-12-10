import unittest

import datetime
import dominate

from args_parser import ArgsParser
import man2html_translator
from man_process_state import ManProcessState
from dominate.tags import *


class Man2HtmlProcessorTests(unittest.TestCase):
    def setUp(self):
        self.translator = man2html_translator.Man2HtmlTranslator(ArgsParser())
        # время не должно меняться в течение одного теста
        man2html_translator.now = lambda: datetime.datetime(1, 1, 1, 1, 1, 1)

    def empty_man_page_html(self):
        return self.man_page_html("", "", "", "", "")

    def man_page_html(self, content, title="", manual="", section="",
                      source="", date=""):
        current_time = man2html_translator.now()
        doc = dominate.document()
        doc.set_title("Man page for {}".format(title))
        doc.add("Section: {} ({})".format(manual, section),
                br(),
                "Source: {}".format(source),
                br(),
                "Updated: {}".format(date),
                hr())
        if content is None or len(content) == 0:
            doc.add(p())
        else:
            doc.add(content)
        doc.add(hr(), current_time.strftime("Time: %H:%M:%S %Z, %B %d, %Y"))
        expected = doc.render()
        return expected

    def test_empty_man_page_should_translate_to_default_empty_html_page(self):
        lines = []
        expected = self.empty_man_page_html()

        actual = self.translator.translate(lines)

        self.assertEqual(expected, actual)

    def test_handle_th_stores_args_in_state(self):
        line = ".TH title section date source manual"
        args = ArgsParser().parse_args(line)
        state = ManProcessState()

        man2html_translator.Man2HtmlTranslator.handle_th(state, [],
                                                         *(args[1:]))

        self.assertEqual("title", state.title)
        self.assertEqual("section", state.section)
        self.assertEqual("date", state.date)
        self.assertEqual("source", state.source)
        self.assertEqual("manual", state.manual)

    def test_th_arguments_should_be_placed_in_html(self):
        lines = [".TH title section date source manual"]
        expected = self.man_page_html([], "title", "manual", "section",
                                      "source", "date")

        actual = self.translator.translate(lines)

        self.assertEqual(expected, actual)

    def test_sh_macros_adds_h2_tag_with_corresponding_content(self):
        lines = [".SH \"SECTION NAME\""]
        expected = self.man_page_html([h2("SECTION NAME")])

        actual = self.translator.translate(lines)

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
