from ase import Atoms

from internal.structures import MLABSection, MLABConfiguration


def configuration_to_atoms(conf: MLABConfiguration) -> Atoms:
    return Atoms(
        symbols=conf.generate_type_lookup(),
        positions=conf.positions,
        cell=conf.lattice_vectors,
        pbc=True,
    )

def section_to_atoms(section: MLABSection) -> list[Atoms]:
    atoms = section.generate_type_lookup()

    return [Atoms(
        symbols=atoms,
        positions=conf.positions,
        cell=conf.lattice_vectors,
        pbc=True,
    ) for conf in section.configurations]
