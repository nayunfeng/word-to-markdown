import re

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


HEADING_PATTERNS = [
    (re.compile(r'^第[一二三四五六七八九十百千万0-9]+[章节部分篇条]\s*'), 1),
    (re.compile(r'^[一二三四五六七八九十]+[、.]\s*'), 1),
    (re.compile(r'^\(?[一二三四五六七八九十]+\)\s*'), 2),
    (re.compile(r'^[0-9]+[、.]\s*'), 2),
    (re.compile(r'^[0-9]+\.[0-9]+\s+'), 2),
    (re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+\s+'), 3),
    (re.compile(r'^\([0-9]+\)\s*'), 3),
]


def iter_block_items(parent):
    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl

    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def _parse_heading_level_from_style(style_name):
    style_name = (style_name or '').strip().lower()
    if 'heading' not in style_name:
        return None
    suffix = style_name.replace('heading', '').strip()
    if not suffix:
        return 1
    digits = ''.join(ch for ch in suffix if ch.isdigit())
    return int(digits) if digits else 1


def _guess_heading_level(text, paragraph):
    for pattern, level in HEADING_PATTERNS:
        if pattern.match(text):
            return level

    # 启发式：短句、无句号、加粗比例高，可能是标题
    text_len = len(text)
    if text_len <= 30:
        no_end_punct = not text.endswith(('。', '.', ';', '；', ':', '：', '!', '！', '?', '？'))
        runs = paragraph.runs or []
        bold_chars = sum(len((run.text or '').strip()) for run in runs if run.bold)
        total_chars = sum(len((run.text or '').strip()) for run in runs)
        bold_ratio = (bold_chars / total_chars) if total_chars else 0
        if no_end_punct and bold_ratio >= 0.6:
            return 2

    return None


def _is_list_paragraph(paragraph, style_name, text):
    if 'list' in style_name:
        return True
    if text.startswith(('•', '-', '*', '·')):
        return True
    p_pr = paragraph._p.pPr
    if p_pr is not None and p_pr.numPr is not None:
        return True
    return False


def _parse_paragraph(paragraph):
    text = paragraph.text.strip()
    if not text:
        return None

    style_name = (paragraph.style.name or '').strip().lower()

    heading_level = _parse_heading_level_from_style(style_name)
    if heading_level is None:
        heading_level = _guess_heading_level(text, paragraph)
    if heading_level is not None:
        return {'type': 'heading', 'level': heading_level, 'text': text}

    if _is_list_paragraph(paragraph, style_name, text):
        clean_text = text.lstrip('•*-· ').strip()
        return {'type': 'list', 'items': [clean_text]}

    return {'type': 'paragraph', 'text': text}


def _parse_table(table):
    rows = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            parts = []
            for paragraph in cell.paragraphs:
                p_text = paragraph.text.strip()
                if p_text:
                    parts.append(p_text)
            row_data.append('\n'.join(parts))
        if any(cell.strip() for cell in row_data):
            rows.append(row_data)

    if not rows:
        return None

    max_cols = max(len(row) for row in rows)
    normalized_rows = [row + [''] * (max_cols - len(row)) for row in rows]
    return {'type': 'table', 'rows': normalized_rows}


def _merge_adjacent_lists(elements):
    merged = []
    for el in elements:
        if el['type'] == 'list' and merged and merged[-1]['type'] == 'list':
            merged[-1]['items'].extend(el.get('items', []))
        else:
            merged.append(el)
    return merged


def parse_docx(path):
    doc = Document(path)
    elements = []

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            parsed = _parse_paragraph(block)
            if parsed:
                elements.append(parsed)
        elif isinstance(block, Table):
            parsed = _parse_table(block)
            if parsed:
                elements.append(parsed)

    return _merge_adjacent_lists(elements)
