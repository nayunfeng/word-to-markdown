import unittest

from src.word_to_markdown.markdown_writer_v3 import to_markdown


class TestMarkdownWriterV3(unittest.TestCase):
    def test_render_heading_paragraph_and_list(self):
        elements = [
            {'type': 'heading', 'level': 1, 'text': '第一章 总则'},
            {'type': 'paragraph', 'text': '这是正文。'},
            {'type': 'list', 'items': ['事项A', '事项B']},
        ]
        md = to_markdown(elements)
        self.assertIn('# 第一章 总则', md)
        self.assertIn('这是正文。', md)
        self.assertIn('- 事项A', md)
        self.assertIn('- 事项B', md)

    def test_render_table(self):
        elements = [
            {
                'type': 'table',
                'rows': [
                    ['列1', '列2'],
                    ['A', 'B'],
                ],
            }
        ]
        md = to_markdown(elements)
        self.assertIn('| 列1 | 列2 |', md)
        self.assertIn('| --- | --- |', md)
        self.assertIn('| A | B |', md)

    def test_render_inline_image(self):
        elements = [
            {'type': 'paragraph', 'text': '图片如下：'},
            {'type': 'image', 'rel_id': 'rId5'},
        ]
        image_map = {
            'rId5': {
                'filename': 'image_001.png',
                'relative_path': 'media/image_001.png',
            }
        }
        md = to_markdown(elements, image_map=image_map)
        self.assertIn('图片如下：', md)
        self.assertIn('![image_001](media/image_001.png)', md)


if __name__ == '__main__':
    unittest.main()
