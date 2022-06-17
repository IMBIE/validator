"""
script to unpack JSON submission document
"""
import argparse as ap
import os

from validator.core.unpack import unpack


def create_parser(name: str, desc: str) -> ap.ArgumentParser:
    """
    create CLI argument parser
    """

    def is_dir(path: str) -> str:
        assert os.path.isdir(path), f"{path} is not a directory"
        return path

    parser = ap.ArgumentParser(name, description=desc)
    parser.add_argument(
        "input",
        type=ap.FileType("r"),
        metavar="SUBMISSION",
        help="JSON format submission data",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=is_dir,
        metavar="PATH",
        help="root output directory",
        default=".",
    )

    return parser


def main() -> None:
    parser = create_parser(__name__, "IMBIE3 submission unpacker")
    args = parser.parse_args()

    for output in unpack(args.input.name, args.out):
        print(f"unpacked {output.fieldname}, created {output.filename}")
