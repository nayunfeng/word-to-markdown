import os
from pathlib import Path

from .parser_v4 import parse_docx
from .markdown_writer_v2 import to_markdown
from .splitter_v2 import split_by_heading as split_func


def convert_one_docx(input_path, output_dir, split_by_heading=False, heading_level=1):
    elements = parse_docx(str(input_path))

    os.makedirs(output_dir, exist_ok=True)
    full_md = to_markdown(elements)
    full_path = os.path.join(output_dir, 'full.md')

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(full_md)

    print(f'Generated: {full_path}')

    if split_by_heading:
        split_func(elements, heading_level, output_dir)
        print(f'Split completed: {output_dir}')


def convert_docx_to_markdown(input_path, output_dir, split_by_heading=False, heading_level=1, recursive=False):
    input_path = Path(input_path)

    if input_path.is_file():
        return convert_one_docx(input_path, output_dir, split_by_heading, heading_level)

    pattern = '**/*.docx' if recursive else '*.docx'
    files = sorted(input_path.glob(pattern))
    if not files:
        print(f'No .docx files found: {input_path}')
        return

    for file_path in files:
        target_dir = Path(output_dir) / file_path.stem
        convert_one_docx(file_path, str(target_dir), split_by_heading, heading_level)
