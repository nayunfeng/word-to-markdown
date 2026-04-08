def _escape_table_cell(text):
    return (text or '').replace('|', '\\|').replace('\n', '<br>')


def _table_to_markdown(rows):
    if not rows:
        return ''

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    lines = []
    lines.append('| ' + ' | '.join(_escape_table_cell(cell) for cell in header) + ' |')
    lines.append('| ' + ' | '.join('---' for _ in header) + ' |')

    for row in body:
        lines.append('| ' + ' | '.join(_escape_table_cell(cell) for cell in row) + ' |')

    return '\n'.join(lines)


def _image_to_markdown(image_info, rel_id=None):
    if not image_info:
        alt_text = rel_id or 'image'
        return f'![{alt_text}]()'

    filename = image_info.get('filename', 'image')
    rel_path = image_info.get('relative_path', '')
    alt_text = filename.rsplit('.', 1)[0]
    return f'![{alt_text}]({rel_path})'


def to_markdown(elements, image_map=None):
    image_map = image_map or {}
    lines = []

    for el in elements:
        if el['type'] == 'heading':
            prefix = '#' * el['level']
            lines.append(f"{prefix} {el['text']}")
        elif el['type'] == 'paragraph':
            lines.append(el['text'])
        elif el['type'] == 'list':
            for item in el.get('items', []):
                clean_item = item.strip()
                lines.append(f'- {clean_item}')
        elif el['type'] == 'table':
            lines.append(_table_to_markdown(el.get('rows', [])))
        elif el['type'] == 'image':
            rel_id = el.get('rel_id')
            lines.append(_image_to_markdown(image_map.get(rel_id), rel_id))

    return '\n\n'.join(line for line in lines if line)
