import os
import re

from .markdown_writer_v2 import to_markdown


def _safe_filename(name):
    name = re.sub(r'[\\/:*?"<>|]+', '_', (name or '').strip())
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:80] or 'untitled'


def split_by_heading(elements, level, output_dir):
    sections = []
    current = None

    for el in elements:
        if el['type'] == 'heading' and el['level'] == level:
            if current:
                sections.append(current)
            current = {'title': el['text'], 'content': [el]}
        else:
            if current:
                current['content'].append(el)

    if current:
        sections.append(current)

    section_dir = os.path.join(output_dir, 'sections')
    os.makedirs(section_dir, exist_ok=True)

    for idx, sec in enumerate(sections, 1):
        filename = f"{idx:03d}-{_safe_filename(sec['title'])}.md"
        path = os.path.join(section_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(to_markdown(sec['content']))
