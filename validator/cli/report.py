import argparse as ap
import io
import os
import tempfile
import pdfkit
import sys

from validator.cli.main import DEFAULT_SCHEMA

from validator.core.unpack import from_directory, unpack
from validator.model.contribution import Contribution, FormatError
from validator.model.schema import Schema
from validator.report.report import render_report


def file_or_folder(value: str) -> str:
    if os.path.isfile(value):
        return value
    if os.path.isdir(value):
        return value
    raise ValueError(f"{value} is not a file or directory")


def writeable_file_or_folder(value: str) -> str:
    if os.path.exists(value):
        return value
    dirname = os.path.dirname(value)
    print(f"basename: '{dirname}'")
    if dirname and not os.path.isdir(dirname):
        raise ValueError(f"{value} is not a writable file or directory")
    return value


def create_parser(name: str, desc: str) -> ap.ArgumentParser:
    """
    set up options for CLI parser
    """
    parser = ap.ArgumentParser(name, description=desc)
    parser.add_argument("input", type=file_or_folder, help="data to parse for report")
    parser.add_argument(
        "-o", "--output", type=writeable_file_or_folder, help="location to save output"
    )
    group = parser.add_argument_group("advanced options")
    group.add_argument("--template", type=str, help="report template file")
    group.add_argument(
        "--schema",
        type=ap.FileType("rb"),
        default=io.BytesIO(DEFAULT_SCHEMA),
        help="validation schema file",
    )

    return parser


def main() -> None:
    parser = create_parser(__name__, "IMBIE-3 Submission Report Generator")

    args = parser.parse_args()

    with args.schema as schema:
        schemas = Schema.read_all(schema)

    if os.path.isfile(args.input):
        root_path = tempfile.mkdtemp()
        items = unpack(args.input, root_path)
    else:
        items = from_directory(args.input)

    outpath = args.output
    if outpath is not None and os.path.isdir(args.output):
        name, _ = os.path.splitext(args.input)
        name = os.path.basename(name)
        outpath = os.path.join(args.output, name + ".pdf")

    for item in items:
        data_path = item.filename

        try:
            contribution = Contribution.from_file(data_path, schemas[item.format_name])
        except FormatError as e:
            sys.stderr.write(f"cannot parse file: {data_path}")
            sys.exit(-1)

        report_html = render_report(contribution)

        if outpath is None:
            print(report_html)
        else:
            tmp_file = io.StringIO()
            tmp_file.write(report_html)
            tmp_file.seek(0)

            pdfkit.from_file(tmp_file, outpath)
            print(f"{outpath} created")
