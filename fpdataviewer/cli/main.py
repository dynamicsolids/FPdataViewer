import argparse
import sys
from pathlib import Path
from typing import Optional

from fpdataviewer.cli.main_convert import convert
from fpdataviewer.cli.main_inspect import inspect
from fpdataviewer.cli.main_plot import plot
from fpdataviewer.cli.main_validate import validate


def register_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reads first-principles molecular simulation data and graphs various statistics")
    subparsers = parser.add_subparsers()

    plot_parser = subparsers.add_parser("plot", help="graphs statistics to screen or PDF")
    register_args_plot(plot_parser)
    register_args_io(plot_parser, True, True)
    plot_parser.set_defaults(exec=plot)

    inspect_parser = subparsers.add_parser("inspect", help="summarizes file contents without analysis")
    register_args_inspect(inspect_parser)
    register_args_io(inspect_parser, True, False)
    inspect_parser.set_defaults(exec=inspect)

    convert_parser = subparsers.add_parser("convert", help="converts between file types")
    register_args_convert(convert_parser)
    register_args_io(convert_parser, True, True)
    convert_parser.set_defaults(exec=convert)

    validate_parser = subparsers.add_parser("validate", help="checks for correct file type formatting")
    register_args_validate(validate_parser)
    register_args_io(validate_parser, True, False)
    validate_parser.set_defaults(exec=validate)

    return parser


def register_args_plot(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="path to config file",
        dest="config_file",
    )

    parser.add_argument(
        "--interactive",
        "-x",
        action="store_true",
        help="launches a matplotlib window instead of saving to a file",
        dest="interactive",
    )
    parser.set_defaults(interactive=False)

    parser.add_argument(
        "--skip",
        "-s",
        default=[],
        choices=["rdf", "desc", "img"],
        nargs="*",
        help="skips calculations for radial distribution functions (rdf) or descriptors (desc)",
        dest="skip",
    )

    parser.add_argument(
        "--rasterize",
        "-r",
        action="store_true",
        help="disables vector image format for plots (which can produce large files when many descriptors are included) and uses raster images",
        dest="rasterize",
    )
    parser.set_defaults(rasterize=False)

    parser.add_argument(
        "--strict",
        "-t",
        action="store_true",
        help="validates file before running calculations",
        dest="strict",
    )
    parser.set_defaults(strict=False)


def register_args_inspect(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--strict",
        "-t",
        action="store_true",
        help="validates file before running calculations",
        dest="strict",
    )
    parser.set_defaults(strict=False)


def register_args_convert(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--from",
        "-f",
        default=None,
        help="source format, see ASE (Atomic Simulation Environment) IO formats or use vasp-mlab for VASP MLFF files",
        dest="from_format",
    )

    parser.add_argument(
        "--to",
        "-t",
        default=None,
        help="target format, see ASE (Atomic Simulation Environment) IO formats",
        dest="to_format",
    )

    parser.add_argument(
        "--index",
        "-x",
        default=None,
        help="indices to consider from source, formatted like a numpy slice",
        dest="index",
    )
    parser.set_defaults(strict=False)

    parser.add_argument(
        "--append",
        "-a",
        action="store_true",
        help="append to target instead of overwriting",
        dest="append",
    )
    parser.set_defaults(strict=False)


def register_args_validate(parser: argparse.ArgumentParser) -> None:
    pass


def register_args_io(parser: argparse.ArgumentParser, has_input: bool, has_output: bool) -> None:
    if has_input:
        parser.add_argument(
            "--input",
            "--in",
            "-i",
            default=None,
            metavar="input",
            help="path to input file\nif directory is supplied, looks for file\ndefaults to working directory",
            dest="input_file",
        )

    if has_output:
        parser.add_argument(
            "--output",
            "--out",
            "-o",
            default=None,
            metavar="output",
            help="path to output file",
            dest="output_file",
        )

    parser.set_defaults(has_input=has_input)
    parser.set_defaults(has_output=has_output)


def find_input_file(path: Optional[str]) -> Path:
    actual_path = Path.cwd() if path is None else Path(path)

    if actual_path.is_dir():
        for name in ["ML_AB", "ML_ABN", "ML_ABCAR"]:
            new_path = actual_path / name
            if new_path.is_file():
                return new_path

        raise FileNotFoundError("could not find a valid input file")
    else:
        return actual_path


def find_output_file(input_path: Path, output_path: Optional[str]) -> Path:
    if output_path is None:
        return input_path.with_suffix(".out")
    else:
        return Path(output_path)


def resolve_io(args) -> None:
    if args.has_input:
        args.input_file = find_input_file(args.input_file)

    if args.has_output:
        args.output_file = find_output_file(args.input_file, args.output_file)

        if args.output_file.exists():
            answer = input(f"{args.output_file} already exists and will be overwritten. are you sure you want to continue? [Y/n] ")

            if answer.lower() in ["n", "no"]:
                sys.exit(0)


def main() -> None:
    parser = register_args()
    args = parser.parse_args()

    resolve_io(args)
    args.exec(args)
