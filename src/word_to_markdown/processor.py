from __future__ import annotations

import logging
import os
from pathlib import Path

from word_to_markdown.conversion import ConversionError, prepare_input
from word_to_markdown.models import BatchResult, FileProcessResult
from word_to_markdown.parser import parse_docx
from word_to_markdown.renderer import (
    HeadingNode,
    build_heading_tree,
    flatten_node_summary,
    flatten_subtree,
    max_heading_level,
    render_markdown,
    safe_title,
)
from word_to_markdown.scanner import scan_inputs
from word_to_markdown.utils import ensure_clean_directory, relative_document_output

LOGGER = logging.getLogger(__name__)


class InputValidationError(ValueError):
    """Raised when CLI inputs are invalid."""


def collect_files(input_path: Path, recursive: bool) -> tuple[list[Path], list[str]]:
    warnings: list[str] = []
    if not input_path.exists():
        raise InputValidationError(f"Input path does not exist: {input_path}")

    if input_path.is_file():
        if recursive:
            warnings.append("--recursive is ignored when the input is a single file")
        if input_path.name.startswith("~$"):
            raise InputValidationError(f"Temporary Word lock files are not supported: {input_path.name}")
        if input_path.suffix.lower() not in {".docx", ".doc"}:
            raise InputValidationError(f"Unsupported input file type: {input_path.suffix}")
        return [input_path], warnings

    files = scan_inputs(input_path, recursive=recursive)
    if not files:
        raise InputValidationError(f"No .doc or .docx files were found in: {input_path}")
    return files, warnings


def process_batch(
    input_path: Path,
    output_root: Path,
    recursive: bool,
    split: bool,
    split_level: int,
    extract_images: bool,
    doc_converter: str,
) -> tuple[BatchResult, list[str]]:
    files, warnings = collect_files(input_path=input_path, recursive=recursive)
    results: list[FileProcessResult] = []

    input_root = input_path if input_path.is_dir() else None
    for source in files:
        output_dir = relative_document_output(source=source, output_root=output_root, input_root=input_root)
        result = process_single_file(
            source=source,
            output_dir=output_dir,
            split=split,
            split_level=split_level,
            extract_images=extract_images,
            doc_converter=doc_converter,
        )
        results.append(result)

    return BatchResult(results=results), warnings


def process_single_file(
    source: Path,
    output_dir: Path,
    split: bool,
    split_level: int,
    extract_images: bool,
    doc_converter: str,
) -> FileProcessResult:
    LOGGER.info("Processing %s", source)
    warnings: list[str] = []
    prepared = None

    try:
        prepared = prepare_input(source=source, converter=doc_converter)
        ensure_clean_directory(output_dir)
        media_dir = output_dir / "media"

        parsed = parse_docx(source=prepared.prepared_path, media_dir=media_dir, extract_images=extract_images)
        warnings.extend(parsed.warnings)

        if split:
            export_document_tree(parsed.blocks, output_dir=output_dir)
        else:
            write_markdown_file(
                target=output_dir / "文档概览.md",
                blocks=parsed.blocks,
                output_dir=output_dir,
            )

        if not extract_images and media_dir.exists():
            warnings.append("Media directory was created even though image extraction is disabled")

        return FileProcessResult(source=source, output_dir=output_dir, success=True, warnings=warnings)
    except ConversionError as exc:
        LOGGER.error("Failed to convert %s: %s", source, exc)
        return FileProcessResult(source=source, output_dir=output_dir, success=False, error=str(exc))
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Failed to process %s", source)
        return FileProcessResult(source=source, output_dir=output_dir, success=False, error=str(exc))
    finally:
        if prepared is not None:
            prepared.cleanup()


def export_document_tree(blocks: list, output_dir: Path) -> None:
    tree = build_heading_tree(blocks)
    if tree.content_blocks or not tree.children:
        write_markdown_file(
            target=output_dir / "文档概览.md",
            blocks=tree.content_blocks or blocks,
            output_dir=output_dir,
        )

    for chapter in tree.children:
        export_chapter(chapter=chapter, output_dir=output_dir)


def export_chapter(chapter: HeadingNode, output_dir: Path) -> None:
    chapter_dir = output_dir / safe_title(chapter)
    chapter_dir.mkdir(parents=True, exist_ok=True)

    if max_heading_level(chapter) <= 2 or not chapter.children:
        write_markdown_file(
            target=chapter_dir / f"{safe_title(chapter)}.md",
            blocks=flatten_subtree(chapter),
            output_dir=output_dir,
        )
        return

    if chapter.content_blocks:
        write_markdown_file(
            target=chapter_dir / f"{safe_title(chapter)}.md",
            blocks=flatten_node_summary(chapter),
            output_dir=output_dir,
        )

    for section in chapter.children:
        export_second_level(section=section, chapter_dir=chapter_dir, output_dir=output_dir)


def export_second_level(section: HeadingNode, chapter_dir: Path, output_dir: Path) -> None:
    if not section.children:
        write_markdown_file(
            target=chapter_dir / f"{safe_title(section)}.md",
            blocks=flatten_subtree(section),
            output_dir=output_dir,
        )
        return

    section_dir = chapter_dir / safe_title(section)
    section_dir.mkdir(parents=True, exist_ok=True)

    if section.content_blocks:
        write_markdown_file(
            target=section_dir / f"{safe_title(section)}.md",
            blocks=flatten_node_summary(section),
            output_dir=output_dir,
        )

    for leaf in section.children:
        write_markdown_file(
            target=section_dir / f"{safe_title(leaf)}.md",
            blocks=flatten_subtree(leaf),
            output_dir=output_dir,
        )


def write_markdown_file(target: Path, blocks: list, output_dir: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    image_prefix = os.path.relpath(output_dir / "media", start=target.parent).replace("\\", "/")
    target.write_text(render_markdown(blocks, image_prefix=image_prefix), encoding="utf-8")
