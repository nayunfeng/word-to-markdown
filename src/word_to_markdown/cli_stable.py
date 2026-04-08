import argparse
import os

from .converter_v6 import convert_docx_to_markdown


STABLE_VERSION = 'v6'


def main():
    parser = argparse.ArgumentParser(
        description='Word to Markdown stable entry (currently backed by v6)'
    )
    subparsers = parser.add_subparsers(dest='command')

    convert_parser = subparsers.add_parser('convert')
    convert_parser.add_argument('--input', required=True, help='input .docx file or directory')
    convert_parser.add_argument('--output', required=True, help='output directory')
    convert_parser.add_argument('--split-by-heading', action='store_true')
    convert_parser.add_argument('--heading-level', type=int, default=1)
    convert_parser.add_argument('--recursive', action='store_true', help='scan subdirectories when input is a directory')
    convert_parser.add_argument('--extract-image', action='store_true', help='extract embedded images and place them inline when possible')

    version_parser = subparsers.add_parser('version')
    version_parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    if args.command == 'convert':
        if not os.path.exists(args.input):
            print(f'Input path not found: {args.input}')
            return

        os.makedirs(args.output, exist_ok=True)
        convert_docx_to_markdown(
            input_path=args.input,
            output_dir=args.output,
            split_by_heading=args.split_by_heading,
            heading_level=args.heading_level,
            recursive=args.recursive,
            extract_image=args.extract_image,
        )
    elif args.command == 'version':
        if args.verbose:
            print(f'stable -> {STABLE_VERSION} (converter_v6 / parser_v5 / markdown_writer_v3)')
        else:
            print(STABLE_VERSION)
    else:
        parser.print_help()
