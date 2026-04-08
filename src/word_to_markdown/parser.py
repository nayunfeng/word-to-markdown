from docx import Document


def parse_docx(path):
    doc = Document(path)
    elements = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style = para.style.name.lower()

        if 'heading' in style:
            level = int(style.replace('heading', '').strip() or 1)
            elements.append({'type': 'heading', 'level': level, 'text': text})
        else:
            elements.append({'type': 'paragraph', 'text': text})

    return elements
