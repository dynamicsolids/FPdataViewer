import argparse
import os
import tomllib
from collections import defaultdict

import numpy as np

from mlab.parsing import MLABParser
from mlab.structures import MLABGroup


def register_args(parser: argparse.ArgumentParser):
    parser.add_argument("mlab_path",
                        nargs="?",
                        default=None,
                        metavar="file/dir",
                        help="file to read - if directory is supplied, looks for ML_AB file - defaults to working directory")

    parser.add_argument("-c",
                        "--config",
                        default="config.ini",
                        dest="config_path",
                        metavar="file",
                        help="config file - will be created if it does not exist - defaults to \"mlab_config.json\"")

    parser.add_argument("-s",
                        "--separate",
                        action="store_true",
                        help="produces separate figures for each plot")


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


def override_config(config: dict, args: argparse.Namespace):
    config.update(vars(args))


def print_stats(group: MLABGroup, config: dict):
    atom_repr = ", ".join([f"{name} ({number})" for name, number in group.header.number_of_atoms_per_type])
    energies = [conf.energy for conf in group.configurations]
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    print()
    print(f"###### {group.header.name} ######")
    print(atom_repr)
    print(f"Structures: {len(group.configurations)}")
    print(f"Atoms: {group.header.number_of_atoms}")
    print()
    print(f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV")


def init(parser: argparse.ArgumentParser) -> tuple[list[MLABGroup], dict]:
    register_args(parser)

    args = parser.parse_args()

    # Load config file
    with open(args.config_path, "rb") as file:
        config = tomllib.load(file)

    override_config(config, args)

    # Load MLAB file
    mlab_path = find_mlab_file(args.mlab_path)

    with open(mlab_path, "rt") as file:
        parser = MLABParser(file)
        mlab = parser.read_mlab()
    # problems = list(validate_mlab(mlab))

    # Split MLAB file
    groups = defaultdict(list)

    for conf in mlab.configurations:
        groups[conf.header].append(conf)

    print(f"Found {len(groups)} group{'s' if len(groups) != 1 else ''} of similar structures")

    return [MLABGroup(mlab=mlab,
                      header=header,
                      configurations=confs) for header, confs in groups.items()], config
