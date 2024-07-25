from __future__ import annotations

from ase import Atoms
from ase.stress import voigt_6_to_full_3x3_stress

from fpdataviewer.mlab.mlab import MLABSection, MLABConfiguration, MLAB


def from_configuration(conf: MLABConfiguration) -> Atoms:
    atoms = Atoms(
              symbols=conf.generate_type_lookup(),
              positions=conf.positions,
              cell=conf.lattice_vectors,
              pbc=True,
             )

    if conf.energy is not None:
          atoms.info["energy"]=conf.energy 
    if conf.forces is not None:
          atoms.arrays['forces']=conf.forces
    if conf.stress is not None:
          atoms.info["stress"]=voigt_6_to_full_3x3_stress([conf.stress.xx,
                                                           conf.stress.yy,
                                                           conf.stress.zz, 
                                                           conf.stress.yz, 
                                                           conf.stress.zx, 
                                                           conf.stress.xy])
 
    return atoms

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
