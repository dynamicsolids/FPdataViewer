import argparse
from collections import defaultdict
from itertools import groupby

import numpy as np
from matplotlib import pyplot as plt

from src.analysis import calculate_radial_histogram
from src.parsing import read_mlab
from src.structures import MLAB, MLABConfiguration, MLABConfigurationHeader
from src.validation import validate_mlab

parser = argparse.ArgumentParser()
parser.add_argument("filename")


def view(mlab: MLAB, configuration_header: MLABConfigurationHeader, configurations: list[MLABConfiguration]):
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

    fig_lattice1, ax_lattice1 = plt.subplots()
    fig_lattice2, ax_lattice2 = plt.subplots()
    fig_energy, ax_energy = plt.subplots()
    fig_forces, ax_forces = plt.subplots()
    fig_stress, ax_stress = plt.subplots()

    ax_lattice1.hist([conf.lattice_vectors[0].get_length() for conf in configurations], bins=31)
    ax_lattice1.hist([conf.lattice_vectors[1].get_length() for conf in configurations], bins=31)
    ax_lattice1.hist([conf.lattice_vectors[2].get_length() for conf in configurations], bins=31)

    ax_lattice2.violinplot([[conf.lattice_vectors[0].get_length() for conf in configurations],
                            [conf.lattice_vectors[1].get_length() for conf in configurations],
                            [conf.lattice_vectors[2].get_length() for conf in configurations]],
                           showextrema=True,
                           showmeans=True,
                           vert=False,
                           points=1000,
                           widths=0.9)

    ax_energy.hist([conf.energy for conf in configurations], bins=51)

    ax_forces.hist([abs(force.x) for conf in configurations for force in conf.forces], bins=51)
    ax_forces.hist([abs(force.y) for conf in configurations for force in conf.forces], bins=51)
    ax_forces.hist([abs(force.z) for conf in configurations for force in conf.forces], bins=51)
    ax_forces.hist([force.get_length() for conf in configurations for force in conf.forces], bins=51)

    ax_stress.hist([conf.stress.get_mechanical_pressure() for conf in configurations], bins=51)

    plt.show()


if __name__ == "__main__":
    args = parser.parse_args()

    mlab = read_mlab(args.filename)
    problems = list(validate_mlab(mlab))

    print(problems)

    groups = defaultdict(list)

    for conf in mlab.configurations:
        groups[conf.header].append(conf)

    for header, confs in groups.items():
        view(mlab, header, confs)
