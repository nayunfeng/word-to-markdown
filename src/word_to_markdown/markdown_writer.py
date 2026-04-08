def to_markdown(elements):
    lines = []

    for el in elements:
        if el['type'] == 'heading':
            prefix = '#' * el['level']
            lines.append(f"{prefix} {el['text']}")
        elif el['type'] == 'paragraph':
            lines.append(el['text'])

    return '\n\n'.join(lines)
