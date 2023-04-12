import argparse
import json
import os
from collections import defaultdict

from matplotlib import pyplot as plt

from internal.config import default_config, set_config
from internal.gui.general import display as display_general
from internal.gui.general import display_general_info
from internal.gui.rdf import display as display_rdf
from internal.parsing import MLABParser
from internal.structures import MLABGroup


def register_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="reads ML_AB files and displays various statistics")
    # subparsers = parser.add_subparsers(dest="command", help="display only specific information")
    # subparsers.add_parser("general", help="general information & histograms")
    # subparsers.add_parser("rdf", help="radial distribution functions")
    # subparsers.add_parser("desc", help="SOAP descriptors")

    parser.add_argument("mlab_path",
                        nargs="?",
                        default=None,
                        metavar="file",
                        help="file to read - if directory is supplied, looks for ML_AB file - defaults to working directory")

    parser.add_argument("-c",
                        "--config",
                        default="mlab_config.json",
                        dest="config_path",
                        metavar="file",
                        help="config file - will be created if it does not exist - defaults to \"mlab_config.json\"")

    parser.add_argument("-s",
                        "--separate",
                        action="store_true",
                        help="produces separate figures for each plot")

    modules_group = parser.add_argument_group("modules")
    modules_group.add_argument("-g",
                               "--general",
                               dest="modules_to_show", action="append_const", const="general",
                               help="(only) display general information & histograms")
    modules_group.add_argument("-r",
                               "--rdf",
                               dest="modules_to_show", action="append_const", const="rdf",
                               help="(only) display radial distribution functions")
    modules_group.add_argument("-d",
                               "--descriptors",
                               dest="modules_to_show", action="append_const", const="descriptors",
                               help="(only) display SOAP descriptors")

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


def update_config(config: dict, args: dict):
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
    update_config(config, vars(args))
    set_config(config)

    # Load MLAB file
    mlab_path = find_mlab_file(args.mlab_path)

    with open(mlab_path, "rt") as file:
        parser = MLABParser(file)
        mlab = parser.read_mlab()

    # Validate MLAB file
    # problems = list(validate_mlab(mlab))

    # Split MLAB file
    groups = defaultdict(list)

    for conf in mlab.configurations:
        groups[conf.header].append(conf)

    groups = [MLABGroup(mlab=mlab, header=header, configurations=confs) for header, confs in groups.items()]

    print(f"Found {len(groups)} group{'s' if len(groups) != 1 else ''} of similar structures")

    # Display information
    show_all = config["modules_to_show"] is None or config["modules_to_show"] == []

    for group in groups:
        display_general_info(group)

        if show_all or "general" in config["modules_to_show"]:
            display_general(group)

        if show_all or "rdf" in config["modules_to_show"]:
            display_rdf(group)

    plt.show()
