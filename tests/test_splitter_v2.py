import unittest

from src.word_to_markdown.splitter_v2 import _safe_filename


class TestSplitterV2(unittest.TestCase):
    def test_safe_filename_replaces_invalid_chars(self):
        name = '第一章:系统/设计?*<>|'
        safe = _safe_filename(name)
        self.assertEqual(safe, '第一章_系统_设计_')

    def test_safe_filename_trims_spaces(self):
        name = '   项目   背景   '
        safe = _safe_filename(name)
        self.assertEqual(safe, '项目 背景')

    def test_safe_filename_fallback(self):
        name = '   '
        safe = _safe_filename(name)
        self.assertEqual(safe, 'untitled')


if __name__ == '__main__':
    unittest.main()
