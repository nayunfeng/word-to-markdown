# word-to-markdown

Word `.doc` / `.docx` to Markdown converter with a CLI entry point.

## Quick Start

Install dependencies with `uv`:

```bash
uv sync
```

Run a single document:

```bash
uv run word-to-markdown --input "./docs/demo.docx" --output "./output" --split
```

Run a directory recursively:

```bash
uv run word-to-markdown --input "./docs" --output "./output" --recursive --split
```

Windows can use:

```bat
run.bat --input ".\docs\demo.docx" --output ".\output" --split
```

## Features

- Single file and batch directory processing
- Recursive scan for `.doc` / `.docx`
- `.doc` pre-conversion through LibreOffice or Microsoft Word
- Paragraph, heading, list, table, image extraction
- Tree-based Markdown export by heading hierarchy
- Root overview output as `文档概览.md` when the document has preface content
- Readable logs and exit codes

## Output Layout

With `--split`, the tool exports a document tree directly under the document output directory:

```text
output/
└─ 示例文档/
   ├─ 文档概览.md
   ├─ 报文结构/
   │  └─ 报文结构.md
   ├─ 报文接口/
   │  └─ 薪资代发/
   │     ├─ 代发提交.md
   │     └─ 代发提交结果查询.md
   ├─ 附录/
   │  ├─ 制单状态.md
   │  └─ 其他/
   │     └─ 支付联行信息查询.md
   └─ media/
```

Without `--split`, the tool writes a single `文档概览.md`.

## Notes

- `--split-level` is currently accepted for compatibility, but tree-based export ignores values other than the default behavior.
- `.doc` input is supported through pre-conversion. If Microsoft Word automation is unstable on the machine, convert the file to `.docx` manually first.
- Word temporary lock files such as `~$*.docx` are ignored automatically.
