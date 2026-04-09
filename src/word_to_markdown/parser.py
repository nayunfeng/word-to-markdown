from __future__ import annotations

import hashlib
import re
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from word_to_markdown.models import (
    Block,
    CodeBlock,
    HeadingBlock,
    ImageBlock,
    ListItemBlock,
    NoteBlock,
    ParagraphBlock,
    ParsedDocument,
    TableBlock,
)

HEADING_STYLE_PATTERN = re.compile(r"(?:^|\b)Heading\s*([1-6])(?:\b|$)", re.IGNORECASE)
ZH_HEADING_STYLE_PATTERN = re.compile(r"标题\s*([1-6])")
CHAPTER_PATTERN = re.compile(r"^第[一二三四五六七八九十百千万零0-9]+章(?:\s+.*)?$")
CN_LEVEL1_PATTERN = re.compile(r"^[一二三四五六七八九十]+、.+$")
CN_LEVEL2_PATTERN = re.compile(r"^（[一二三四五六七八九十]+）.+$")
PAREN_NUMBER_PATTERN = re.compile(r"^（\d+）.+$")
UNORDERED_LIST_PATTERN = re.compile(r"^\s*([\-*•])\s+(.+)$")
ORDERED_LIST_PATTERN = re.compile(r"^\s*(\d+)[\.\)]\s+(.+)$")
SENTENCE_ENDING_PATTERN = re.compile(r"[。；.;]$")
TOC_TITLE_PATTERN = re.compile(r"^目\s*录$")
XML_DECLARATION_PATTERN = re.compile(r"^<\?xml\b", re.IGNORECASE)
COMMENT_LINE_PATTERN = re.compile(r"^<!--.*-->$")
ELLIPSIS_LINE_PATTERN = re.compile(r"^(?:\.{3,}|…+)$")
IMAGE_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tif",
}


def parse_docx(source: Path, media_dir: Path, extract_images: bool) -> ParsedDocument:
    document = Document(str(source))
    parsed = ParsedDocument(source=source)
    image_index = 1
    seen_images: dict[str, str] = {}

    for block in iter_block_items(document):
        if isinstance(block, Paragraph):
            if should_skip_paragraph(block):
                continue

            image_blocks, image_warnings, image_index = extract_paragraph_images(
                block,
                media_dir,
                image_index=image_index,
                extract_images=extract_images,
                seen_images=seen_images,
            )
            parsed.warnings.extend(image_warnings)

            text = normalize_text(block.text)
            if text:
                heading_level = detect_heading_level(block, text)
                if heading_level is not None:
                    parsed.blocks.append(HeadingBlock(level=heading_level, text=text))
                else:
                    list_item = detect_list_item(text, block.style.name if block.style else "")
                    if list_item is not None:
                        parsed.blocks.append(list_item)
                    else:
                        parsed.blocks.append(ParagraphBlock(text=text))

            parsed.blocks.extend(image_blocks)
        elif isinstance(block, Table):
            parsed.blocks.append(TableBlock(rows=extract_table_rows(block)))

    parsed.blocks = collapse_code_blocks(parsed.blocks)
    return parsed


def iter_block_items(document: DocumentObject):
    parent_elm = document.element.body
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def normalize_text(value: str) -> str:
    text = value.replace("\r", "").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def detect_heading_level(paragraph: Paragraph, text: str) -> int | None:
    style_name = paragraph.style.name if paragraph.style else ""
    style_level = detect_style_heading_level(style_name)
    if style_level is not None:
        return style_level

    if len(text) > 80 or SENTENCE_ENDING_PATTERN.search(text):
        return None

    if CHAPTER_PATTERN.match(text):
        return 1
    if CN_LEVEL1_PATTERN.match(text):
        return 1
    if CN_LEVEL2_PATTERN.match(text):
        return 2
    if PAREN_NUMBER_PATTERN.match(text):
        return 3

    segments = extract_numbered_segments(text)
    if segments:
        return min(len(segments), 6)

    return None


def should_skip_paragraph(paragraph: Paragraph) -> bool:
    text = normalize_text(paragraph.text)
    style_name = paragraph.style.name if paragraph.style else ""
    normalized_style = normalize_style_name(style_name)

    if TOC_TITLE_PATTERN.match(text):
        return True

    if normalized_style.startswith("toc"):
        return True

    return False


def detect_style_heading_level(style_name: str) -> int | None:
    if not style_name:
        return None

    normalized = normalize_style_name(style_name)
    if normalized.startswith("toc"):
        return None

    match = HEADING_STYLE_PATTERN.search(style_name)
    if match:
        return int(match.group(1))

    zh_match = ZH_HEADING_STYLE_PATTERN.search(style_name)
    if zh_match:
        return int(zh_match.group(1))

    return None


def normalize_style_name(style_name: str) -> str:
    return " ".join(style_name.lower().split())


def extract_numbered_segments(text: str) -> list[str]:
    prefix_match = re.match(r"^(\d+(?:\.\d+)*)", text)
    if not prefix_match:
        return []

    prefix = prefix_match.group(1)
    remainder = text[len(prefix) :]
    if remainder and remainder[0].isalnum():
        return []
    return prefix.split(".")


def detect_list_item(text: str, style_name: str) -> ListItemBlock | None:
    if "List" in style_name:
        return ListItemBlock(text=text, ordered="Number" in style_name)

    unordered_match = UNORDERED_LIST_PATTERN.match(text)
    if unordered_match:
        return ListItemBlock(text=unordered_match.group(2).strip(), ordered=False)

    ordered_match = ORDERED_LIST_PATTERN.match(text)
    if ordered_match:
        return ListItemBlock(text=ordered_match.group(2).strip(), ordered=True)

    return None


def extract_paragraph_images(
    paragraph: Paragraph,
    media_dir: Path,
    image_index: int,
    extract_images: bool,
    seen_images: dict[str, str],
) -> tuple[list[ImageBlock | NoteBlock], list[str], int]:
    blocks: list[ImageBlock | NoteBlock] = []
    warnings: list[str] = []

    if not extract_images:
        return blocks, warnings, image_index

    for relationship_id in paragraph._p.xpath(".//a:blip/@r:embed"):
        image_part = paragraph.part.related_parts[relationship_id]
        image_hash = hashlib.sha1(image_part.blob).hexdigest()
        if image_hash in seen_images:
            filename = seen_images[image_hash]
        else:
            extension = IMAGE_CONTENT_TYPES.get(image_part.content_type, ".bin")
            filename = f"image_{image_index:03d}{extension}"
            image_index += 1
            try:
                media_dir.mkdir(parents=True, exist_ok=True)
                (media_dir / filename).write_bytes(image_part.blob)
                seen_images[image_hash] = filename
            except OSError as exc:
                warnings.append(f"Image extraction failed in {paragraph.part.partname}: {exc}")
                blocks.append(NoteBlock(text=f"image extraction failed: {exc}"))
                continue

        blocks.append(ImageBlock(filename=filename, alt_text=filename))

    return blocks, warnings, image_index


def extract_table_rows(table: Table) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table.rows:
        rows.append([normalize_table_cell(cell.text) for cell in row.cells])
    return rows


def normalize_table_cell(value: str) -> str:
    text = value.replace("\r", "").strip()
    return re.sub(r"\n{2,}", "\n", text)


def collapse_code_blocks(blocks: list[Block]) -> list[Block]:
    collapsed: list[Block] = []
    index = 0

    while index < len(blocks):
        block = blocks[index]
        if isinstance(block, ParagraphBlock) and is_code_block_start(block.text):
            code_lines = [block.text]
            index += 1
            while index < len(blocks):
                current = blocks[index]
                if not isinstance(current, ParagraphBlock) or not is_code_block_line(current.text):
                    break
                code_lines.append(current.text)
                index += 1
            collapsed.append(CodeBlock(code="\n".join(code_lines), language="xml"))
            continue

        collapsed.append(block)
        index += 1

    return collapsed


def is_code_block_start(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("<")


def is_code_block_line(text: str) -> bool:
    stripped = text.lstrip()
    return bool(
        stripped.startswith("<")
        or COMMENT_LINE_PATTERN.match(text)
        or ELLIPSIS_LINE_PATTERN.match(text)
    )
