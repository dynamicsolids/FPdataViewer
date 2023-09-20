from ase import Atoms

from fpdataviewer.mlab.mlab import MLABSection, MLABConfiguration, MLAB


def from_configuration(conf: MLABConfiguration) -> Atoms:
    return Atoms(
        symbols=conf.generate_type_lookup(),
        positions=conf.positions,
        cell=conf.lattice_vectors,
        pbc=True,
    )

def from_section(section: MLABSection) -> list[Atoms]:
    atoms = section.generate_type_lookup()

    return [Atoms(
        symbols=atoms,
        positions=conf.positions,
        cell=conf.lattice_vectors,
        pbc=True,
    ) for conf in section.configurations]

def from_mlab(mlab: MLAB) -> list[Atoms]:
    return [from_configuration(conf) for conf in mlab.configurations]
