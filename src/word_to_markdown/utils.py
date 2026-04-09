from __future__ import annotations

import re
import shutil
from pathlib import Path

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def sanitize_filename(value: str, default: str = "untitled") -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", value).strip().rstrip(".")
    sanitized = re.sub(r"\s+", " ", sanitized)
    if not sanitized:
        sanitized = default
    if sanitized.upper() in WINDOWS_RESERVED_NAMES:
        sanitized = f"{sanitized}_file"
    return sanitized


def ensure_clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return True
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


def relative_document_output(
    source: Path,
    output_root: Path,
    input_root: Path | None,
) -> Path:
    if input_root and input_root.is_dir():
        relative_parent = source.relative_to(input_root).parent
    else:
        relative_parent = Path()
    return output_root / relative_parent / sanitize_filename(source.stem)

