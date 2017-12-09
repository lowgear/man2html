import unittest

from args_parser import ArgsParser


class ArgsParserTests(unittest.TestCase):
    '''Тестирование поведения парсера аргументов Man pages'''
    def setUp(self):
        self.parser = ArgsParser()

    def test_splits_line_by_whitespaces(self):
        line = "word1 word2"
        expected = ["word1", "word2"]

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_excludes_empty_strings(self):
        line = "word1      word2"
        expected = ["word1", "word2"]

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_doesnt_split_text_surrounded_with_double_quotes(self):
        line = '"word1 word2"'
        expected = ["word1 word2"]

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_double_quote_lead_by_nonwhitespace_char_is_not_opening(self):
        line = 'word1" word2"'
        expected = ['word1"', 'word2"']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_unclosed_double_quote_is_text(self):
        line = 'word1 "word2'
        expected = ['word1', '"word2']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_closing_double_quote_should_be_text(self):
        line = 'word1 "word2'
        expected = ['word1', '"word2']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_two_double_quotes_in_row_represent_empty_arg(self):
        line = 'word1 "" word2'
        expected = ['word1', '', 'word2']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_closing_double_quote_followed_by_nonwhitespace_closes(self):
        line = 'word1 "word"2'
        expected = ['word1', 'word', '2']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)

    def test_escaped_e_should_turn_into_backslash(self):
        line = 'word1\\e'
        expected = ['word1\\']

        parsed = self.parser.parse_args(line)

        self.assertEqual(expected, parsed)


if __name__ == "__main__":
    unittest.main()
