import os


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

    os.makedirs(os.path.join(output_dir, 'sections'), exist_ok=True)

    for idx, sec in enumerate(sections, 1):
        filename = f"{idx:03d}-{sec['title']}.md"
        path = os.path.join(output_dir, 'sections', filename)

        with open(path, 'w', encoding='utf-8') as f:
            for el in sec['content']:
                if el['type'] == 'heading':
                    f.write('#' * el['level'] + ' ' + el['text'] + '\n\n')
                else:
                    f.write(el['text'] + '\n\n')
