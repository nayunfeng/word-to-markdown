import unittest

from src.word_to_markdown.parser_v4 import _guess_heading_level


class FakeRun:
    def __init__(self, text, bold=False):
        self.text = text
        self.bold = bold


class FakeParagraph:
    def __init__(self, runs):
        self.runs = runs


class TestParserV4Rules(unittest.TestCase):
    def test_guess_heading_for_chinese_numbering(self):
        paragraph = FakeParagraph([FakeRun('第一章 总则', bold=False)])
        level = _guess_heading_level('第一章 总则', paragraph)
        self.assertEqual(level, 1)

    def test_guess_heading_for_section_numbering(self):
        paragraph = FakeParagraph([FakeRun('1.1 系统架构', bold=False)])
        level = _guess_heading_level('1.1 系统架构', paragraph)
        self.assertEqual(level, 2)

    def test_guess_heading_for_bold_short_text(self):
        paragraph = FakeParagraph([FakeRun('项目背景', bold=True)])
        level = _guess_heading_level('项目背景', paragraph)
        self.assertEqual(level, 2)

    def test_non_heading_sentence_should_return_none(self):
        paragraph = FakeParagraph([FakeRun('这是一个完整的说明句子。', bold=False)])
        level = _guess_heading_level('这是一个完整的说明句子。', paragraph)
        self.assertIsNone(level)


if __name__ == '__main__':
    unittest.main()
