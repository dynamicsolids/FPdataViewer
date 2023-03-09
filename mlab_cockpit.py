import argparse
import os
from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from parsing import read_mlab
from structures import MLAB, MLABConfiguration, MLABConfigurationHeader

parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="?", default=os.getcwd())


# TODO: Restructure project to have top-level scripts


def view(mlab: MLAB, configuration_header: MLABConfigurationHeader, configurations: list[MLABConfiguration]):
    # TODO: Format graphs
    # TODO: Try different
    # TODO: Move to using style sheets?

    atom_repr = ", ".join([f"{name} ({number})" for name, number in configuration_header.number_of_atoms_per_type])
    energies = [conf.energy for conf in configurations]
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    # hist = calculate_radial_histogram(configuration_header,
    #                                   configurations,
    #                                   set(["Li"]),
    #                                   set(["Li"]),
    #                                   10,
    #                                   100)
    # plt.bar(*zip(*hist))
    # plt.show()

    print()
    print()
    print(f"Name:       {configuration_header.name}")
    print(f"Structures: {len(configurations)}")
    print(f"Atoms:      {atom_repr}")
    print(f"Total:      {configuration_header.number_of_atoms}")
    print()
    print(f"Mean energy: {mean_energy:.1f}")
    print(f"Std energy:  {std_energy:.2f}")

    # fig_lattice, ax_lattice = plt.subplots()
    # fig_energy, ax_energy = plt.subplots()
    # fig_forces, ax_forces = plt.subplots()
    # fig_stress, ax_stress = plt.subplots()
    fig = plt.figure(layout="tight")
    spec = fig.add_gridspec(ncols=2, nrows=2)
    ax_lattice = fig.add_subplot(spec[0, 0])
    ax_energy = fig.add_subplot(spec[0, 1])
    ax_forces = fig.add_subplot(spec[1, 0])
    ax_stress = fig.add_subplot(spec[1, 1])

    ax_lattice.hist([conf.lattice_vectors[0].get_length() for conf in configurations],
                    bins=31, label="a", alpha=0.8)
    ax_lattice.hist([conf.lattice_vectors[1].get_length() for conf in configurations],
                    bins=31, label="b", alpha=0.8)
    ax_lattice.hist([conf.lattice_vectors[2].get_length() for conf in configurations],
                    bins=31, label="c", alpha=0.8)
    ax_lattice.set_xlabel("Lattice vector length [ang]")
    ax_lattice.legend()
    ax_lattice.grid(True)

    ax_energy.hist([conf.energy for conf in configurations],
                   bins=51, color="k")
    ax_energy.set_xlabel("Energy [eV]")
    ax_energy.grid(True)

    ax_forces.hist([abs(force.x) for conf in configurations for force in conf.forces],
                   bins=51, label="x", color="r", alpha=0.7)
    ax_forces.hist([abs(force.y) for conf in configurations for force in conf.forces],
                   bins=51, label="y", color="b", alpha=0.7)
    ax_forces.hist([abs(force.z) for conf in configurations for force in conf.forces],
                   bins=51, label="z", color="g", alpha=0.7)
    ax_forces.hist([force.get_length() for conf in configurations for force in conf.forces],
                   bins=51, label="||.||", color="k", alpha=0.7)
    ax_forces.set_xlabel("Force [eV/ang]")
    ax_forces.legend()
    ax_forces.grid(True)

    ax_stress.hist([conf.stress.get_mechanical_pressure() for conf in configurations],
                   bins=51, color="k")
    ax_stress.set_xlabel("Mechanical pressure [kbar]")
    ax_stress.grid(True)

    plt.show()


def find_mlab_file(path: str) -> str:
    if os.path.isfile(path):
        return path

    if os.path.isdir(path):
        names_to_look_for = ["ML_AB", "ML_ABN", "ML_ABCAR"]

        for name in names_to_look_for:
            new_path = os.path.join(path, name)
            if os.path.isfile(new_path):
                return new_path

    raise FileNotFoundError()


if __name__ == "__main__":
    # TODO: Implement (non-)grouping option
    # TODO: Implement option to split window
    # TODO: Handle validation output

    args = parser.parse_args()

    path = find_mlab_file(args.path)
    mlab = read_mlab(path)
    # problems = list(validate_mlab(mlab))

    groups = defaultdict(list)

    for conf in mlab.configurations:
        groups[conf.header].append(conf)

    for header, confs in groups.items():
        view(mlab, header, confs)
