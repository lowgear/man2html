import argparse
import gzip
import logging
import os
import pathlib
import sys

from core.args_parser import ArgsParser
from core.man2html_translator import Man2HtmlTranslator

__version__ = "1.0"
__author__ = 'Aidar Islamov'
__email__ = 'lowgear1000@gmail.com'

ERROR_EXCEPTION = 1

GZ_SUFFIX = '.gz'


def get_man_path():
    try:
        with open(MANPATH_CONFIG_PATH, 'r') as f:
            result = []
            for line in f:
                line = line.strip()
                if line[0] == '#':
                    continue
                parts = line.split(maxsplit=3)
                mapping = parts[0]
                if mapping == "MANDATORY_MANPATH" and len(parts) >= 2:
                    result.append(parts[1])
                elif mapping == "MANPATH_MAP" and len(parts) >= 3 and \
                        parts[1] in sys.path:
                    result.append(parts[2])
        return result
    except:
        return []


MANPATH_CONFIG_PATH = pathlib.Path('/etc/manpath.config')
MAN_PATH = get_man_path()


def parse_args():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Man pages to HTML translator. Version {}".format(
            __version__),
        epilog="Author {} [{}]".format(__author__, __email__)
    )

    parser.add_argument(
        "name",
        metavar='NAME',
        type=str,
        help="Man page name or input file to translate")

    parser.add_argument(
        "-s",
        "--section",
        metavar='SECTION',
        type=int,
        default=1,
        help="Man page section")

    parser.add_argument(
        "-e",
        "--encoding",
        metavar='ENCODING',
        type=str,
        default="utf-8",
        help="Input file encoding")

    parser.add_argument(
        "-o",
        "--output",
        metavar='OUTPUT',
        type=str,
        default=None,
        help="Output file path. stdout of not specified")

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Output file path. stdout of not specified")

    parser.add_argument(
        "--output-encoding",
        metavar='OUTPUT_ENCODING',
        type=str,
        default="utf-8",
        help="Output file encoding")

    return parser.parse_args()


def get_file_from_man_path(name: str, section: int):
    if not section or section < 1 or section > 8:
        return None

    file_name = name + '.' + str(section) + '.gz'
    section = "man" + str(section)
    for directory in MAN_PATH:
        possible_path = pathlib.Path(directory, section, file_name)
        if possible_path.is_file() and os.access(str(possible_path), os.R_OK):
            return possible_path


def main():
    args = parse_args()

    log = logging.StreamHandler(sys.stderr)
    log.setFormatter(logging.Formatter(
        "%(name)s: %(asctime)s [%(levelname)s] %(message)s"))

    translator = Man2HtmlTranslator(ArgsParser(), strict_mode=args.strict)

    input_file = get_file_from_man_path(args.name, args.section)
    if not input_file:
        input_file = args.name
    try:
        input_stream = open_man_file(input_file, args.encoding)
    except OSError as e:
        print("Error opening file.\n{}".format(e), file=sys.stderr)
        sys.exit(ERROR_EXCEPTION)
    else:
        pass  # todo log input OK

    with input_stream as f:
        try:
            result = translator.translate(f)
        except NotImplementedError as e:
            print("Not implemented:\n{0}".format(e), file=sys.stderr)
            sys.exit(ERROR_EXCEPTION)
        except Exception as e:
            # todo log error
            print("Some error happened", file=sys.stderr)
            raise e
        else:
            pass  # todo log translation OK

    print_result(result, args)
    # todo log finished OK


def open_man_file(name, encoding):
    path = pathlib.Path(name)
    suffix = path.suffix.lower()
    if suffix == GZ_SUFFIX:
        return gzip.open(name, 'rt', encoding=encoding)
    return open(name, encoding=encoding)


def print_result(result, args):
    if args.output:
        try:
            with open(args.output, 'w',
                      encoding=args.output_encoding) as output:
                output.write(result)
        except:
            print("Error writing to {}".format(args.output), file=sys.stderr)
            sys.exit(ERROR_EXCEPTION)  # todo is it proper way?
    else:
        print(result)


if __name__ == "__main__":
    main()
