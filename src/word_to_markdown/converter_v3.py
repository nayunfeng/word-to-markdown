import os

from .parser_v3 import parse_docx
from .markdown_writer_v2 import to_markdown
from .splitter_v2 import split_by_heading as split_func


def convert_docx_to_markdown(input_path, output_dir, split_by_heading=False, heading_level=1):
    elements = parse_docx(input_path)

    full_md = to_markdown(elements)
    full_path = os.path.join(output_dir, 'full.md')

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(full_md)

    print(f'Generated: {full_path}')

    if split_by_heading:
        split_func(elements, heading_level, output_dir)
        print('Split completed')
