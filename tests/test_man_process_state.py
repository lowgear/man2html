import unittest

from core.man_process_state import ManProcessState


class ManProcessStateTests(unittest.TestCase):
    def test_empty_man_page_should_translate_to_default_empty_html_page(self):
        state = ManProcessState()

        self.assertEqual("", state.title)
        self.assertEqual("", state.section)
        self.assertEqual("", state.date)
        self.assertEqual("", state.source)
        self.assertEqual("", state.manual)


if __name__ == "__main__":
    unittest.main()
