
from __future__ import annotations

import numpy as np

from fpdataviewer.mlab import parsing, validation
from fpdataviewer.mlab.mlab import MLAB, MLABBasisSet


def filter(args) -> None:
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)

    cutoff = 0.05
    keep = []

    for i, conf in enumerate(mlab.configurations):
        lattice_parameters = np.linalg.norm(conf.lattice_vectors, axis=1)
        average_parameter = np.average(lattice_parameters)
        deviations = np.abs(lattice_parameters - average_parameter) / average_parameter

        if np.max(deviations) < cutoff:
            keep.append(i)

    try:
        validation.validate(mlab)
    except validation.ValidationException as e:
        print("for original:")
        print(e)
        return

    print(f"{len(mlab.configurations)} -> {len(keep)} ({len(mlab.configurations) - len(keep)} will be removed)")

    if len(keep) == 0:
        print("no configurations will be left!")
        return

    mlab.configurations = [conf for i, conf in enumerate(mlab.configurations) if i in keep]
    for i, conf in enumerate(mlab.configurations):
        conf.index = i + 1
    mlab.number_of_configurations = len(keep)

    for set in mlab.basis_sets:
        set.indices = np.array([(keep.index(ic - 1) + 1, ia) for ic, ia in set.indices if ic - 1 in keep])
    mlab.numbers_of_basis_sets = [len(set.indices) for set in mlab.basis_sets]

    # remember the indices in the basis sets are 1-based
    #new_confs = [conf
    #             for i, conf in enumerate(mlab.configurations)
    #             if i in keep]
    #new_basis = [MLABBasisSet(name=set.name, indices=set.indices[np.isin(set.indices[:, 0] - 1, keep)])
    #             for set in mlab.basis_sets]
    #new_basis = [MLABBasisSet(name=set.name, 
    #                          indices=np.array([(keep.index(i_conf - 1) + 1, i_atom)
    #                                            for (i_conf, i_atom) in set.indices
    #                                            if i_conf - 1 in keep]))
    #             for set in mlab.basis_sets]

    # assume atoms stay same
    #new_mlab = MLAB(number_of_configurations=len(new_confs),
    #                max_number_of_atom_types=mlab.max_number_of_atom_types,
    #                atom_types=mlab.atom_types,
    #                max_number_of_atoms_per_system=mlab.max_number_of_atoms_per_system,
    #                max_number_of_atoms_per_type=mlab.max_number_of_atoms_per_type,
    #                reference_energies=mlab.reference_energies,
    #                atomic_masses=mlab.atomic_masses,
    #                numbers_of_basis_sets=[len(set.indices)
    #                                       for set in new_basis],
    #                basis_sets=new_basis,
    #                configurations=new_confs)

    try:
        validation.validate(mlab)
    except validation.ValidationException as e:
        print("for new:")
        print(e)
        return

    with args.output_file.open(mode="w") as file:
        parsing.write(file, mlab)
