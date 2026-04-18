"""
JSON Parser CLI entry point.

This module provides a command-line interface for the jsonparser package, allowing
users to parse JSON files and see the resulting Python objects.
"""

__version__ = "0.1.0"

import argparse
import logging
import os
import pickle
import pprint
import sys
import time

from .parser import JsonParser
from .errors import JsonParserError, JsonLexerError

def setup_logging(level: str, filename: str = None):
    """
    Sets up logging for the script.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logging.basicConfig(
        level=numeric_level,
        format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=filename,
        filemode='w'
    )

def parse_args(args):
    """
    Sets up argparse and defines the command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-l", "--log",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        help="Path to a file where logs will be written instead of the console"
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Suppress all output to the console (except timing if requested)"
    )
    parser.add_argument(
        "-t", "--time",
        action="store_true",
        help="Time the parsing operation and report the duration (to stderr)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to a file where the parsed Python object will be written"
    )
    parser.add_argument(
        "-p", "--pickle",
        action="store_true",
        help="Serialize output with pickle. If --output is omitted, writes to [input_file].pkl"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType('r', encoding='utf-8'),
        default=sys.stdin,
        help="The JSON file to parse (reads from stdin if omitted)"
    )
    return parser.parse_args(args)

def main(args):
    """
    The main entry point for the script.
    """
    parsed_args = parse_args(args)
    setup_logging(parsed_args.log, parsed_args.log_file)

    logger = logging.getLogger(__name__)
    logger.debug("Starting JSON parser CLI.")

    # Determine the effective output path
    output_path = parsed_args.output
    if parsed_args.pickle and not output_path:
        # If reading from stdin, we use a generic name, otherwise we base it on the input filename.
        if parsed_args.file is sys.stdin:
            output_path = "output.pkl"
        else:
            output_path = os.path.splitext(parsed_args.file.name)[0] + ".pkl"

    try:
        content = parsed_args.file.read()

        parser = JsonParser(content)

        start_time = time.perf_counter()
        result = parser.parse()
        duration = time.perf_counter() - start_time

        if parsed_args.time:
            print(f"Parsing completed in {duration:.6f} seconds.", file=sys.stderr)

        if output_path:
            if parsed_args.pickle:
                with open(output_path, "wb") as f:
                    pickle.dump(result, f)
                logger.info("Pickled output written to %s", output_path)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    pprint.pprint(result, stream=f)
                logger.info("Pretty-printed output written to %s", output_path)
        
        # Only print to console if no output (explicit or automatic) was requested
        if not parsed_args.silent and not output_path:
            pprint.pprint(result)

        return 0

    except (JsonParserError, JsonLexerError) as e:
        logger.error("Parse error: %s", e)
        return 1
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
        return 1
    finally:
        if parsed_args.file is not sys.stdin:
            parsed_args.file.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
