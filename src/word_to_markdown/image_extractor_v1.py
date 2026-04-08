import os
from pathlib import Path

from docx import Document


IMAGE_REL_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'


def _safe_ext(content_type, default='.bin'):
    mapping = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/tiff': '.tiff',
        'image/x-emf': '.emf',
        'image/x-wmf': '.wmf',
        'image/svg+xml': '.svg',
    }
    return mapping.get((content_type or '').lower(), default)


def extract_images(input_path, output_dir):
    doc = Document(input_path)
    media_dir = Path(output_dir) / 'media'
    media_dir.mkdir(parents=True, exist_ok=True)

    images = []
    seen = set()

    for rel in doc.part.rels.values():
        if rel.reltype != IMAGE_REL_TYPE:
            continue

        image_part = rel.target_part
        blob = image_part.blob
        if not blob:
            continue

        digest = (len(blob), getattr(image_part, 'partname', ''))
        if digest in seen:
            continue
        seen.add(digest)

        ext = _safe_ext(getattr(image_part, 'content_type', None))
        filename = f'image_{len(images) + 1:03d}{ext}'
        target = media_dir / filename

        with open(target, 'wb') as f:
            f.write(blob)

        images.append({
            'filename': filename,
            'relative_path': f'media/{filename}',
            'content_type': getattr(image_part, 'content_type', None),
        })

    return images


def images_to_markdown(images, title='## Images'):
    if not images:
        return ''

    lines = [title]
    for image in images:
        alt_text = os.path.splitext(image['filename'])[0]
        lines.append(f"![{alt_text}]({image['relative_path']})")

    return '\n\n'.join(lines)
