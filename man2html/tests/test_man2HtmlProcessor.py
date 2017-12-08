import unittest

from man2html_processor import Man2HtmlProcessor


class TestMan2HtmlProcessorParseManArgs(unittest.TestCase):
    '''Тестирование поведения парсера аргументов Man pages'''
    def setUp(self):
        self.parse_man_args = Man2HtmlProcessor.\
            _Man2HtmlProcessor__parse_man_args

    def test_splits_line_by_whitespaces(self):
        line = "word1 word2"
        expected = ["word1", "word2"]

        parsed = self.parse_man_args(line)

        self.assertEqual(expected, parsed)

    def test_excludes_empty_strings(self):
        line = "word1      word2"
        expected = ["word1", "word2"]

        parsed = self.parse_man_args(line)

        self.assertEqual(expected, parsed)

    def test_doesnt_split_text_surrounded_with_double_quotes(self):
        line = '"word1 word2"'
        expected = ["word1 word2"]

        parsed = self.parse_man_args(line)

        self.assertEqual(expected, parsed)


if __name__ == "__main__":
    unittest.main()
