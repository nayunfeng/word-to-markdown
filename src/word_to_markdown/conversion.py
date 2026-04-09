from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

LIBREOFFICE_TIMEOUT_SECONDS = 120
WORD_AUTOMATION_TIMEOUT_SECONDS = 60


class ConversionError(RuntimeError):
    """Raised when a legacy .doc file cannot be converted."""


@dataclass(slots=True)
class PreparedInput:
    source: Path
    prepared_path: Path
    temporary_dir: tempfile.TemporaryDirectory[str] | None = None

    def cleanup(self) -> None:
        if self.temporary_dir is not None:
            self.temporary_dir.cleanup()


def prepare_input(source: Path, converter: str = "auto") -> PreparedInput:
    suffix = source.suffix.lower()
    if suffix == ".docx":
        return PreparedInput(source=source, prepared_path=source)
    if suffix != ".doc":
        raise ConversionError(f"Unsupported input type: {source.suffix}")

    temp_dir = tempfile.TemporaryDirectory(prefix="word-to-markdown-")
    temp_path = Path(temp_dir.name)
    converted_path = temp_path / f"{source.stem}.docx"

    strategy = select_converter(converter)
    if strategy == "libreoffice":
        convert_with_libreoffice(source, temp_path)
    elif strategy == "word":
        convert_with_word(source, converted_path)
    else:
        temp_dir.cleanup()
        raise ConversionError("No available converter found for .doc files")

    if not converted_path.exists():
        temp_dir.cleanup()
        raise ConversionError(f"Converted file was not produced for {source.name}")

    return PreparedInput(source=source, prepared_path=converted_path, temporary_dir=temp_dir)


def select_converter(converter: str) -> str | None:
    if converter == "libreoffice":
        if find_libreoffice_command():
            return "libreoffice"
        raise ConversionError("LibreOffice/soffice is not available")
    if converter == "word":
        return "word"
    if converter != "auto":
        raise ConversionError(f"Unsupported converter option: {converter}")

    if find_libreoffice_command():
        return "libreoffice"
    if shutil.which("powershell"):
        return "word"
    return None


def find_libreoffice_command() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def convert_with_libreoffice(source: Path, output_dir: Path) -> None:
    command = find_libreoffice_command()
    if not command:
        raise ConversionError("LibreOffice/soffice is not available")

    try:
        result = subprocess.run(
            [
                command,
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(output_dir),
                str(source),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=LIBREOFFICE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError(
            f"LibreOffice conversion timed out after {LIBREOFFICE_TIMEOUT_SECONDS}s for {source.name}"
        ) from exc
    if result.returncode != 0:
        raise ConversionError(result.stderr.strip() or result.stdout.strip() or "LibreOffice conversion failed")


def convert_with_word(source: Path, target: Path) -> None:
    if not shutil.which("powershell"):
        raise ConversionError("PowerShell is not available for Microsoft Word conversion")

    script = f"""
$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {{
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.Options.SaveNormalPrompt = $false
    $document = $word.Documents.Open(
        '{escape_ps_path(source)}',
        [ref] $false,
        [ref] $true,
        [ref] $false
    )
    $document.SaveAs2([ref] '{escape_ps_path(target)}', [ref] 16)
}}
finally {{
    if ($document -ne $null) {{
        $document.Close([ref] 0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }}
    if ($word -ne $null) {{
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }}
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}}
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=WORD_AUTOMATION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError(
            "Microsoft Word automation timed out after "
            f"{WORD_AUTOMATION_TIMEOUT_SECONDS}s while converting {source.name}. "
            "Please close residual WINWORD processes and retry, or convert this file to .docx manually."
        ) from exc
    if result.returncode != 0:
        raise ConversionError(result.stderr.strip() or result.stdout.strip() or "Microsoft Word conversion failed")


def escape_ps_path(path: Path) -> str:
    return str(path).replace("'", "''")
