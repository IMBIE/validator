import argparse as ap
import sys
import pkgutil
import io
import json
from validator.const.severity import ExitCode, Severity

from validator.model.schema import Schema
from validator.core.validate import validate_file

DEFAULT_SCHEMA = pkgutil.get_data("validator.data", "schema.yml")


def create_parser(name: str, description: str) -> ap.ArgumentParser:
    """
    setup and return CLI argument parser
    """
    p = ap.ArgumentParser(name, description=description)
    p.add_argument(
        "input",
        metavar="DATA_FILE",
        type=ap.FileType("rb"),
        help="CSV contribution file to validate",
    )
    p.add_argument(
        "-f",
        "--format",
        metavar="FORMAT",
        required=True,
        type=str,
        help="name of file format schema to use",
    )
    p.add_argument(
        "-s",
        "--schema",
        metavar="SCHEMA",
        type=ap.FileType("rb"),
        default=io.BytesIO(DEFAULT_SCHEMA),
        help="IMBIE validation schema file (will use default if omitted)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=ap.FileType("w"),
        default=sys.stdout,
        metavar="OUTPUT_PATH",
        help="location to save output data",
    )
    p.add_argument("-j", "--json", action="store_true", help="JSON format output")
    return p


def main() -> None:
    parser = create_parser(__name__, "IMBIE3 validation tool")
    args = parser.parse_args()

    with args.schema as schema:
        schema = Schema.from_file(schema, args.format)

    exit_code = ExitCode.ok

    with args.input as infile:
        messages = list(validate_file(infile, schema))
    for message in messages:
        if message.severity == Severity.error:
            exit_code = ExitCode.validation_failed

    if args.json:
        json.dump([m.to_json() for m in messages], args.output, indent=2)
    else:
        for message in messages:
            print(f"title: {message.title}", file=args.output)
            print(f"severity: {message.severity}", file=args.output)
            print(f"description: {message.description}", file=args.output)

    sys.exit(exit_code.value)
