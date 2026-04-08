import argparse
import os

from .converter_v3 import convert_docx_to_markdown


def main():
    parser = argparse.ArgumentParser(description='Word to Markdown tool v3')
    subparsers = parser.add_subparsers(dest='command')

    convert_parser = subparsers.add_parser('convert')
    convert_parser.add_argument('--input', required=True, help='input docx file')
    convert_parser.add_argument('--output', required=True, help='output directory')
    convert_parser.add_argument('--split-by-heading', action='store_true')
    convert_parser.add_argument('--heading-level', type=int, default=1)

    args = parser.parse_args()

    if args.command == 'convert':
        if not os.path.exists(args.input):
            print(f'Input file not found: {args.input}')
            return

        os.makedirs(args.output, exist_ok=True)

        convert_docx_to_markdown(
            input_path=args.input,
            output_dir=args.output,
            split_by_heading=args.split_by_heading,
            heading_level=args.heading_level
        )
    else:
        parser.print_help()
