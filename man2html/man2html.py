import argparse
import logging
import sys

from args_parser import ArgsParser
from man2html_translator import Man2HtmlTranslator

__version__ = "1.0"
__author__ = 'Aidar Islamov'
__email__ = 'lowgear1000@gmail.com'


ERROR_EXCEPTION = 1


def parse_args():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Man pages to HTML translator. Version {}".format(
            __version__),
        epilog="Author {} [{}]".format(__author__, __email__)
    )

    parser.add_argument(
        "input_file",
        metavar='INPUT',
        type=str,
        help="Input file to translate")

    parser.add_argument(
        "-e",
        "--encoding",
        metavar='ENCODING',
        type=str,
        default="utf-8",
        help="Input file encoding")

    return parser.parse_args()


def main():
    args = parse_args()

    log = logging.StreamHandler(sys.stderr)
    log.setFormatter(logging.Formatter(
        "%(name)s: %(asctime)s [%(levelname)s] %(message)s"))

    translator = Man2HtmlTranslator(ArgsParser())

    try:
        input_stream = open(args.input_file, encoding=args.encoding)
    except OSError as e:
        print("Error opening file.\n{}".format(e), file=sys.stderr)
        sys.exit(ERROR_EXCEPTION)
    else:
        pass  # todo log input OK

    with input_stream as f:
        try:
            result = translator.translate(f)
        except Exception as e:
            # todo log error
            print("Some error happened\n{}".format(e), file=sys.stderr)
            sys.exit(ERROR_EXCEPTION)
        else:
            pass  # todo log translation OK

    print(result, file=sys.stdout)

    # todo log finished OK


if __name__ == "__main__":
    main()
