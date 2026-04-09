from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Block:
    kind: str


@dataclass(slots=True)
class HeadingBlock(Block):
    level: int
    text: str

    def __init__(self, level: int, text: str) -> None:
        Block.__init__(self, kind="heading")
        self.level = level
        self.text = text


@dataclass(slots=True)
class ParagraphBlock(Block):
    text: str

    def __init__(self, text: str) -> None:
        Block.__init__(self, kind="paragraph")
        self.text = text


@dataclass(slots=True)
class ListItemBlock(Block):
    text: str
    ordered: bool

    def __init__(self, text: str, ordered: bool) -> None:
        Block.__init__(self, kind="list_item")
        self.text = text
        self.ordered = ordered


@dataclass(slots=True)
class TableBlock(Block):
    rows: list[list[str]]

    def __init__(self, rows: list[list[str]]) -> None:
        Block.__init__(self, kind="table")
        self.rows = rows


@dataclass(slots=True)
class CodeBlock(Block):
    code: str
    language: str

    def __init__(self, code: str, language: str = "") -> None:
        Block.__init__(self, kind="code")
        self.code = code
        self.language = language


@dataclass(slots=True)
class ImageBlock(Block):
    filename: str
    alt_text: str

    def __init__(self, filename: str, alt_text: str) -> None:
        Block.__init__(self, kind="image")
        self.filename = filename
        self.alt_text = alt_text


@dataclass(slots=True)
class NoteBlock(Block):
    text: str

    def __init__(self, text: str) -> None:
        Block.__init__(self, kind="note")
        self.text = text


@dataclass(slots=True)
class ParsedDocument:
    source: Path
    blocks: list[Block] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FileProcessResult:
    source: Path
    output_dir: Path
    success: bool
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def partial_success(self) -> bool:
        return self.success and bool(self.warnings)


@dataclass(slots=True)
class BatchResult:
    results: list[FileProcessResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for item in self.results if item.success and not item.warnings)

    @property
    def partial_count(self) -> int:
        return sum(1 for item in self.results if item.partial_success)

    @property
    def failure_count(self) -> int:
        return sum(1 for item in self.results if not item.success)

    @property
    def has_warnings_or_failures(self) -> bool:
        return any((not item.success) or item.warnings for item in self.results)
