from __future__ import annotations

from dataclasses import dataclass, field

from word_to_markdown.models import (
    Block,
    CodeBlock,
    HeadingBlock,
    ImageBlock,
    ListItemBlock,
    NoteBlock,
    ParagraphBlock,
    TableBlock,
)
from word_to_markdown.utils import sanitize_filename


@dataclass(slots=True)
class HeadingNode:
    level: int
    title: str
    content_blocks: list[Block] = field(default_factory=list)
    children: list["HeadingNode"] = field(default_factory=list)


def render_markdown(blocks: list[Block], image_prefix: str) -> str:
    lines: list[str] = []
    index = 0
    while index < len(blocks):
        block = blocks[index]
        if isinstance(block, HeadingBlock):
            lines.extend([f"{'#' * block.level} {block.text}", ""])
        elif isinstance(block, ParagraphBlock):
            lines.extend([block.text, ""])
        elif isinstance(block, ListItemBlock):
            marker_index = 1
            while index < len(blocks) and isinstance(blocks[index], ListItemBlock):
                current = blocks[index]
                assert isinstance(current, ListItemBlock)
                marker = f"{marker_index}." if current.ordered else "-"
                lines.append(f"{marker} {current.text}")
                marker_index += 1
                index += 1
            lines.append("")
            continue
        elif isinstance(block, TableBlock):
            lines.extend(render_table(block))
            lines.append("")
        elif isinstance(block, CodeBlock):
            info = block.language.strip()
            lines.extend([f"```{info}", block.code, "```", ""])
        elif isinstance(block, ImageBlock):
            lines.extend([f"![{block.alt_text}]({build_image_reference(image_prefix, block.filename)})", ""])
        elif isinstance(block, NoteBlock):
            lines.extend([f"<!-- {block.text} -->", ""])
        index += 1

    return "\n".join(lines).strip() + "\n"


def build_heading_tree(blocks: list[Block]) -> HeadingNode:
    root = HeadingNode(level=0, title="root")
    stack: list[HeadingNode] = [root]

    for block in blocks:
        if isinstance(block, HeadingBlock):
            while stack and stack[-1].level >= block.level:
                stack.pop()
            parent = stack[-1] if stack else root
            node = HeadingNode(level=block.level, title=block.text)
            parent.children.append(node)
            stack.append(node)
        else:
            stack[-1].content_blocks.append(block)

    return root


def has_structured_sections(blocks: list[Block]) -> bool:
    return any(isinstance(block, HeadingBlock) and block.level == 1 for block in blocks)


def flatten_subtree(node: HeadingNode) -> list[Block]:
    blocks: list[Block] = [HeadingBlock(level=node.level, text=node.title)]
    blocks.extend(node.content_blocks)
    for child in node.children:
        blocks.extend(flatten_subtree(child))
    return blocks


def flatten_node_summary(node: HeadingNode) -> list[Block]:
    blocks: list[Block] = [HeadingBlock(level=node.level, text=node.title)]
    blocks.extend(node.content_blocks)
    return blocks


def max_heading_level(node: HeadingNode) -> int:
    levels = [node.level]
    for child in node.children:
        levels.append(max_heading_level(child))
    return max(levels)


def safe_title(node: HeadingNode) -> str:
    return sanitize_filename(node.title)


def render_table(table: TableBlock) -> list[str]:
    if not table.rows:
        return []

    normalized_rows = pad_rows(table.rows)
    header = [escape_table_cell(cell) for cell in normalized_rows[0]]
    separator = ["---"] * len(header)
    lines = [
        f"| {' | '.join(header)} |",
        f"| {' | '.join(separator)} |",
    ]
    for row in normalized_rows[1:]:
        lines.append(f"| {' | '.join(escape_table_cell(cell) for cell in row)} |")
    if len(normalized_rows) == 1:
        lines.append(f"| {' | '.join([''] * len(header))} |")
    return lines


def pad_rows(rows: list[list[str]]) -> list[list[str]]:
    width = max((len(row) for row in rows), default=0)
    return [row + [""] * (width - len(row)) for row in rows]


def escape_table_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", "<br>")


def build_image_reference(prefix: str, filename: str) -> str:
    cleaned_prefix = prefix.replace("\\", "/").rstrip("/")
    if not cleaned_prefix:
        return filename
    return f"{cleaned_prefix}/{filename}"
