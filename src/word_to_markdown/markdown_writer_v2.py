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


def to_markdown(elements):
    lines = []

    for el in elements:
        if el['type'] == 'heading':
            prefix = '#' * el['level']
            lines.append(f"{prefix} {el['text']}")
        elif el['type'] == 'paragraph':
            lines.append(el['text'])
        elif el['type'] == 'list':
            for item in el.get('items', []):
                clean_item = item.lstrip('•*-· ').strip()
                lines.append(f'- {clean_item}')
        elif el['type'] == 'table':
            lines.append(_table_to_markdown(el.get('rows', [])))

    return '\n\n'.join(line for line in lines if line)
