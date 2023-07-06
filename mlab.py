import argparse
import json
import os
import sys

from rich.prompt import Confirm

from internal import parsing, analysis
from internal.config import default_config, set_config
from internal.output import output_console


def register_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reads ML_AB files and displays various statistics")
    # subparsers = parser.add_subparsers(dest="command", help="display only specific information")
    # subparsers.add_parser("general", help="general information & histograms")
    # subparsers.add_parser("rdf", help="radial distribution functions")
    # subparsers.add_parser("desc", help="SOAP descriptors")

    parser.add_argument("-i",
                        "--input",
                        default=None,
                        dest="mlab_path",
                        metavar="file",
                        help="file to read - if directory is supplied, looks for ML_AB file - defaults to working directory")

    parser.add_argument("-o",
                        "--output",
                        choices=["matplotlib", "dash", "none"],
                        default="matplotlib",
                        dest="output",
                        help="method used to display results")

    parser.add_argument("-c",
                        "--config",
                        default="mlab_config.json",
                        dest="config_path",
                        metavar="file",
                        help="config file - will be created if it does not exist - defaults to \"mlab_config.json\"")

    # modules_group = parser.add_argument_group("modules")
    # modules_group.add_argument("-G",
    #                            "--general",
    #                            dest="modules_to_show", action="append_const", const="general",
    #                            help="(only) display general information & histograms")
    # modules_group.add_argument("-R",
    #                            "--rdf",
    #                            dest="modules_to_show", action="append_const", const="rdf",
    #                            help="(only) display radial distribution functions")
    # modules_group.add_argument("-D",
    #                            "--descriptors",
    #                            dest="modules_to_show", action="append_const", const="descriptors",
    #                            help="(only) display SOAP descriptors")

    return parser


def find_mlab_file(path: str | None) -> str:
    if path is None:
        path = os.getcwd()

    if os.path.isfile(path):
        return path

    if os.path.isdir(path):
        names_to_look_for = ["ML_AB", "ML_ABN", "ML_ABCAR"]

        for name in names_to_look_for:
            new_path = os.path.join(path, name)
            if os.path.isfile(new_path):
                return new_path

    raise FileNotFoundError()


def merge_config(config: dict, args: dict):
    for key, value in args.items():
        if "." in key:
            key, subkey = key.split(".")

            sub_dict = config.get(key, {})
            sub_dict[subkey] = value
        else:
            config[key] = value


if __name__ == "__main__":
    # Load arguments
    args = register_args().parse_args()

    # Load config file
    if os.path.isfile(args.config_path):
        with open(args.config_path, "rt") as file:
            config = json.load(file)
    else:
        config = default_config
        with open(args.config_path, "wt") as file:
            json.dump(config, file, indent=4)

    # Merge arguments into config
    merge_config(config, vars(args))
    set_config(config)

    # Load MLAB file
    mlab_path = find_mlab_file(args.mlab_path)

    with open(mlab_path, "rt") as file:
        mlab = parsing.load(file)

    # Validate MLAB file
    # problems = list(validate_mlab(mlab))

    sections = parsing.split(mlab)

    if len(sections) > 1:
        print(f"File seems to contain {len(sections)} groups of structures")

    if len(sections) > 4:
        should_continue = Confirm.ask("Each section will be analysed separately. Are you sure you want to continue? [Y/n]",
                                      default=True,
                                      show_choices=False,
                                      show_default=False)

        if not should_continue:
            sys.exit()

    # Display information
    if args.output == "matplotlib":
        import internal.output.output_matplotlib as output
    elif args.output == "dash":
        import internal.output.output_dash as output
    else:
        output = None

    for i, section in enumerate(sections):
        stats = analysis.get_stats(section)

        output_console.run((i + 1, len(sections)), section, stats)

        if output is not None:
            output.run(section, stats)
