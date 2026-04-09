# word-to-markdown

Word `.doc` / `.docx` to Markdown converter with a CLI entry point.

## Quick Start

```bash
python -m word_to_markdown --input "./docs/demo.docx" --output "./output" --split
```

Windows can use:

```bat
run.bat --input ".\docs\demo.docx" --output ".\output"
```

## Features

- Single file and batch directory processing
- Recursive scan for `.doc` / `.docx`
- `.doc` pre-conversion through LibreOffice or Microsoft Word
- Paragraph, heading, list, table, image extraction
- Tree-based Markdown export by heading hierarchy
- Root overview output as `文档概览.md` when the document has preface content
- Readable logs and exit codes
