from __future__ import annotations

import argparse
import logging
from pathlib import Path

from word_to_markdown.processor import InputValidationError, process_batch
from word_to_markdown.utils import parse_bool

LOGGER = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        split = parse_bool(args.split)
        recursive = parse_bool(args.recursive)
        extract_images = parse_bool(args.extract_images)
    except ValueError as exc:
        parser.error(str(exc))

    if args.split_level not in {1, 2}:
        parser.error("--split-level must be 1 or 2")

    configure_logging(log_file=Path(args.log_file) if args.log_file else None)

    if not split:
        LOGGER.warning("--split-level is ignored because --split is disabled")
    elif args.split_level != 1:
        LOGGER.warning("--split-level is currently ignored by tree-based section export")

    try:
        batch, runtime_warnings = process_batch(
            input_path=Path(args.input).expanduser().resolve(),
            output_root=Path(args.output).expanduser().resolve(),
            recursive=recursive,
            split=split,
            split_level=args.split_level,
            extract_images=extract_images,
            doc_converter=args.doc_converter,
        )
    except InputValidationError as exc:
        LOGGER.error("%s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Unexpected runtime error")
        LOGGER.error("%s", exc)
        return 3

    for warning in runtime_warnings:
        LOGGER.warning("%s", warning)

    for result in batch.results:
        if result.success:
            level = logging.WARNING if result.warnings else logging.INFO
            LOGGER.log(level, "Processed %s -> %s", result.source, result.output_dir)
            for warning in result.warnings:
                LOGGER.warning("%s", warning)
        else:
            LOGGER.error("Failed %s: %s", result.source, result.error)

    LOGGER.info(
        "Summary: total=%s success=%s partial=%s failed=%s",
        batch.total,
        batch.success_count,
        batch.partial_count,
        batch.failure_count,
    )

    if batch.failure_count == 0 and not batch.has_warnings_or_failures and not runtime_warnings:
        return 0
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Word files to Markdown")
    parser.add_argument("--input", required=True, help="Input file or directory path")
    parser.add_argument("--output", required=True, help="Output root directory")
    parser.add_argument("--split", nargs="?", const=True, default=False, help="Enable section splitting")
    parser.add_argument("--split-level", type=int, default=1, help="Split heading level: 1 or 2")
    parser.add_argument("--recursive", nargs="?", const=True, default=False, help="Recursively scan directories")
    parser.add_argument(
        "--extract-images",
        nargs="?",
        const=True,
        default=True,
        help="Whether to extract embedded images",
    )
    parser.add_argument("--log-file", help="Optional log file path")
    parser.add_argument(
        "--doc-converter",
        default="auto",
        choices=["auto", "word", "libreoffice"],
        help="Converter used for legacy .doc files",
    )
    return parser


def configure_logging(log_file: Path | None) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
