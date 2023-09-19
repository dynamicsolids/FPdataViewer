import argparse
import sys
from pathlib import Path

import src.convert
import src.inspect
import src.plot
import src.validate


def register_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reads ML_AB-like files and displays various statistics")
    subparsers = parser.add_subparsers(help="sub-command help")

    plot_parser = subparsers.add_parser("plot")
    register_args_plot(plot_parser)
    register_args_io(plot_parser, True, True)
    plot_parser.set_defaults(exec=src.plot.exec)

    inspect_parser = subparsers.add_parser("inspect")
    register_args_inspect(inspect_parser)
    register_args_io(inspect_parser, True, False)
    inspect_parser.set_defaults(exec=src.inspect.exec)

    convert_parser = subparsers.add_parser("convert")
    register_args_convert(convert_parser)
    register_args_io(convert_parser, True, True)
    convert_parser.set_defaults(exec=src.convert.exec)

    validate_parser = subparsers.add_parser("validate")
    register_args_validate(validate_parser)
    register_args_io(validate_parser, True, False)
    validate_parser.set_defaults(exec=src.validate.exec)

    return parser


def register_args_plot(parser: argparse.ArgumentParser):
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
        help="",
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


def register_args_io(parser: argparse.ArgumentParser, has_input: bool, has_output: bool):
    if has_input:
        parser.add_argument(
            "--input",
            "--in",
            "-i",
            default=None,
            metavar="input file",
            help="path to input file\nif directory is supplied, looks for file\ndefaults to working directory",
            dest="input_file",
        )

    if has_output:
        parser.add_argument(
            "--output",
            "--out",
            "-o",
            default=None,
            metavar="output file",
            help="path to output file",
            dest="output_file",
        )

    parser.set_defaults(has_input=has_input)
    parser.set_defaults(has_output=has_output)


def find_input_file(path: str | None) -> Path:
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)

    if path.is_file():
        return path
    elif path.is_dir():
        look_for = ["ML_AB", "ML_ABN", "ML_ABCAR"]

        for name in look_for:
            new_path = path / name
            if new_path.is_file():
                return new_path

        raise FileNotFoundError("could not find a valid input file")


def find_output_file(input_path: Path, output_path: str | None) -> Path:
    if output_path is None:
        return input_path.with_suffix(".out")
    else:
        return Path(output_path)


def resolve_io(args):
    if args.has_input:
        args.input_file = find_input_file(args.input_file or args.pos_args[0])

    if args.has_output:
        args.output_file = find_output_file(args.input_file, args.output_file or args.pos_args[1])

        if args.output_file.exists():
            answer = input(f"{args.output_file} already exists and will be overwritten. are you sure you want to continue? [Y/n] ")

            if answer.lower() in ["n", "no"]:
                sys.exit(0)



if __name__ == "__main__":
    # Parse arguments
    parser = register_args()
    args = parser.parse_args()

    resolve_io(args)
    args.exec(args)
