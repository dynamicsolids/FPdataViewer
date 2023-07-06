import numpy as np
from rich import print
from rich.panel import Panel
from rich.text import Text

from internal.structures import MLABSection, MLABSectionStats


def run(section_index: tuple[int, int], section: MLABSection, stats: MLABSectionStats):
    atom_repr = ", ".join([f"{name} ({number})" for name, number in section.common_header.number_of_atoms_per_type])
    energies = [conf.energy for conf in section.configurations]
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    text = Text()
    text.append(f"Name      : {section.name}\n")
    text.append(f"Atoms     : {section.number_of_atoms}\n")
    text.append(f"Atom types: {atom_repr}\n")
    text.append(f"Structures: {len(section.configurations)} out of {len(section.source.configurations)} in file\n")
    text.append("\n")
    text.append(f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV")

    panel = Panel(text, title=f"[{section_index[0]}/{section_index[1]}] {section.name}", title_align="left")

    print(panel)


# def run(section: MLABSection, stats: MLABSectionStats):
#     atom_repr = ", ".join([f"{name} ({number})" for name, number in section.common_header.number_of_atoms_per_type])
#     energies = [conf.energy for conf in section.configurations]
#     mean_energy = np.mean(energies)
#     std_energy = np.std(energies)
#
#     print("------------------------------------------")
#     print(f"Name      : {section.name}")
#     print(f"Atoms     : {section.number_of_atoms}")
#     print(f"Atom types: {atom_repr}")
#     print(f"Structures: {len(section.configurations)} / {len(section.source.configurations)}")
#     print("")
#     print(f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV")
#     print("------------------------------------------")
#
#     # TODO: Bounding box volume (average)
#     # TODO: Bounding box min. non-overlapping sphere radius (average), useful for RDF
