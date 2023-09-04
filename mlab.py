import argparse
import json
import sys
from pathlib import Path

from mlab_tools import parsing
from mlab_viewer.config import default_config, set_config


def register_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reads ML_AB files and displays various statistics")

    parser.add_argument(
        nargs="?",
        metavar="input file",
        action="append",
        dest="pos_args",
        help="path to ML_AB file",
    )

    parser.add_argument(
        nargs="?",
        metavar="output file",
        action="append",
        dest="pos_args",
        help="path for output, format set by --mode",
    )

    parser.add_argument(
        "-i",
        "--in",
        "--input",
        default=None,
        metavar="input file (ML_AB)",
        help="path to input file (ML_AB file)\nif directory is supplied, looks for ML_AB file\ndefaults to working directory",
        dest="input_file",
    )

    parser.add_argument(
        "-o",
        "--out",
        "--output",
        default=None,
        metavar="output file",
        help="path to output file (unused if --mode none)",
        dest="output_file",
    )

    parser.add_argument(
        "-c",
        "--conf",
        "--config",
        default=None,
        help="path to config file",
        dest="config_file",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["pdf", "plt", "none"],
        default="pdf",
        help="output format. pdf (pdf), matplotlib plot (plot), or only print to console (none)",
        dest="mode",
    )

    parser.add_argument(
        "-s",
        "--skip",
        default=[],
        choices=["rdf", "desc", "img"],
        nargs="*",
        help="skips calculations for radial distribution functions (rdf) or descriptors (desc)",
        dest="skip",
    )

    parser.add_argument(
        "-r",
        "--raster",
        "--rasterize",
        action="store_true",
        help="disables vector image format for plots (which can produce large files when many descriptors are included) and uses raster images",
        dest="rasterize",
    )
    parser.set_defaults(rasterize=False)

    return parser


def find_mlab_file(path: str | None) -> Path:
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)

    if path.is_file():
        return path
    elif path.is_dir():
        names_to_look_for = ["ML_AB", "ML_ABN", "ML_ABCAR"]

        for name in names_to_look_for:
            new_path = path / name
            if new_path.is_file():
                return new_path

    raise FileNotFoundError("could not find ML_AB file")


def find_output_file(input_path: Path, output_path: str | None) -> Path:
    if output_path is None:
        return input_path.with_suffix(".pdf")
    else:
        return Path(output_path)


if __name__ == "__main__":
    # Parse arguments
    parser = register_args()
    args = parser.parse_args()

    if args.pos_args[0] is not None and args.input_file is not None:
        parser.error(f"supplied two input paths (\"{args.pos_args[0]}\" and \"{args.input_file}\")")
    elif args.pos_args[1] is not None and args.output_file is not None:
        parser.error(f"supplied two output paths (\"{args.pos_args[1]}\" and \"{args.output_file}\")")

    args.input_file = find_mlab_file(args.input_file or args.pos_args[0])
    args.output_file = find_output_file(args.input_file, args.output_file or args.pos_args[1])

    if args.mode == "pdf" and args.output_file.exists():
        answer = input(f"{args.output_file} already exists and will be overwritten. are you sure you want to continue? [Y/n] ")

        if answer.lower() in ["n", "no"]:
            sys.exit(0)


    # Load config file
    config = default_config

    if args.config_file is not None:
        with args.config_file.open(mode="rt") as file:
            config.update(json.load(file))
    # else:
    #     with open(args.config_path, "wt") as file:
    #         json.dump(config, file, indent=4)

    set_config(config)

    # Load MLAB file
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)
    # problems = list(validate_mlab(mlab))
    sections = parsing.split(mlab)

    # Prompt user for confirmation when many sections are found
    print(f"file contains {len(sections)} group{'' if len(sections) == 1 else 's'} of structures")

    if len(sections) > 2:
        answer = input("each group will be analysed separately and to different files. are you sure you want to continue? [Y/n] ")

        if answer.lower() in ["n", "no"]:
            sys.exit(0)

    print()
    for i, section in enumerate(sections):
        atom_repr = ", ".join([f"{name} ({number})" for name, number in section.number_of_atoms_per_type])
        current_group = i + 1
        total_groups = len(sections)

        print(f"[{current_group}/{total_groups}] name       : {section.name}")
        print(f"[{current_group}/{total_groups}] atoms      : {section.number_of_atoms}")
        print(f"[{current_group}/{total_groups}] atom types : {atom_repr}")
        print(f"[{current_group}/{total_groups}] structures : {len(section.configurations)} / {len(section.source.configurations)}")
        print()

    if args.mode == "plt":
        import mlab_viewer.output.output_plt as output
    elif args.mode == "pdf":
        import mlab_viewer.output.output_pdf as output
    else:
        output = None

    if output is not None:
        output.run(args, mlab, sections)

        print("\r")
