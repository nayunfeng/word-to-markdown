from pathlib import Path

from docx import Document


IMAGE_REL_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


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

    image_map = {}
    seq = 1

    for rel_id, rel in doc.part.rels.items():
        if rel.reltype != IMAGE_REL_TYPE:
            continue

        image_part = rel.target_part
        blob = image_part.blob
        if not blob:
            continue

        ext = _safe_ext(getattr(image_part, 'content_type', None))
        filename = f'image_{seq:03d}{ext}'
        seq += 1

        target = media_dir / filename
        with open(target, 'wb') as f:
            f.write(blob)

        image_map[rel_id] = {
            'filename': filename,
            'relative_path': f'media/{filename}',
            'content_type': getattr(image_part, 'content_type', None),
        }

    return image_map


def paragraph_image_rel_ids(paragraph):
    rel_ids = []
    seen = set()

    for run in paragraph.runs:
        drawing_elements = run._element.xpath('.//a:blip', namespaces=NS)
        for blip in drawing_elements:
            rel_id = blip.get('{%s}embed' % NS['r'])
            if rel_id and rel_id not in seen:
                seen.add(rel_id)
                rel_ids.append(rel_id)

    return rel_ids
