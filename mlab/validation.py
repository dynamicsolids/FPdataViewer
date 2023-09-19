from typing import Any

from mlab.mlab import MLAB


class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


def _error(message: str) -> ValidationException:
    return ValidationException(f"problem validating file: {message}")


def _assert_eq(reported: Any, expected: Any, message: str):
    if reported != expected:
        raise _error(message.format(reported, expected))

def _validate_global(mlab: MLAB):
    # Numbers
    _assert_eq(mlab.number_of_configurations,
               len(mlab.configurations),
               "\'The number of configurations\' is {0} but {1} were found")

    _assert_eq(mlab.max_number_of_atom_types,
               len(mlab.atom_types),
               "\'The maximum number of atom type\' is {0} but {1} are named")

    _assert_eq(mlab.max_number_of_atoms_per_system,
               max(conf.number_of_atoms for conf in mlab.configurations),
               "\'The maximum number of atoms per system\' is {0} but the maximum is {1}")

    _assert_eq(mlab.max_number_of_atoms_per_type,
               max(amount for conf in mlab.configurations for _, amount in conf.number_of_atoms_per_type),
               "\'The maximum number of atoms per atom type\' is {0} but the maximum is {1}")

    # Atom types
    _assert_eq(len(mlab.atom_types),
               len(set(mlab.atom_types)),
               "\'The atom types in the data file\' contains duplicate elements")

    _assert_eq(set(mlab.atom_types),
               {atom_type for conf in mlab.configurations for atom_type, _ in conf.number_of_atoms_per_type},
               "\'The atom types in the data file\' are {0}, but {1} were found")

    # Per-atom-type values
    _assert_eq(len(mlab.reference_energies),
               len(mlab.atom_types),
               "\'Reference atomic energy\' contains {0} items but {1} types were named")

    _assert_eq(len(mlab.atomic_masses),
               len(mlab.atom_types),
               "\'Atomic mass\' contains {0} items but {1} types were named")

    _assert_eq(len(mlab.numbers_of_basis_sets),
               len(mlab.atom_types),
               "\'The numbers of basis sets per atom type\' contains {0} items but {1} types were named")


def _validate_configurations(mlab: MLAB):
    for i, conf in enumerate(mlab.configurations):
        if conf.index != i + 1:
            raise _error(f"configurations are not indexed sequentially ({i + 1}'s configuration has index {conf.index})")

        _assert_eq(conf.number_of_atom_types,
                   len(conf.number_of_atoms_per_type),
                   f"in configuration {conf.index}, \'The number of atom types\' is {0} but {1} are named")

        _assert_eq(len({name for name, _ in conf.number_of_atoms_per_type}),
                   conf.number_of_atom_types,
                   f"in configuration {conf.index}, \'Atom types and atom numbers\' contains duplicate elements")

        _assert_eq(sum([amount for _, amount in conf.number_of_atoms_per_type]),
                   conf.number_of_atoms,
                   f"in configuration {conf.index}, \'Atom types and atom numbers\' has a total of {0} atoms, but {1} only exist")

        _assert_eq(conf.lattice_vectors.shape,
                   (3, 3),
                   f"in configuration {conf.index}, \'Primitive lattice vectors (ang.)\' has shape {0} but expected {1}")

        _assert_eq(conf.positions.shape,
                   (conf.number_of_atoms, 3),
                   f"in configuration {conf.index}, \'Atomic positions (ang.)\' has shape {0} but expected {1}")

        _assert_eq(conf.forces.shape,
                   (conf.number_of_atoms, 3),
                   f"in configuration {conf.index}, \'Forces (eV ang.^-1)\' has shape {0} but expected {1}")

        if conf.charges is not None:
            _assert_eq(conf.charges.shape,
                       (conf.number_of_atoms,),
                       f"in configuration {conf.index}, \'Charges (e)\' has shape {0} but expected {1}")


def _validate_basis_sets(mlab: MLAB):
    _assert_eq(len(mlab.basis_sets),
               len({basis_set.name for basis_set in mlab.basis_sets}),
               "duplicate basis sets were found")

    _assert_eq(set(mlab.atom_types),
               {basis_set.name for basis_set in mlab.basis_sets},
               "\'The atom types in the data file\' are {0}, but basis sets are named for {1}")

    for basis_set in mlab.basis_sets:
        _assert_eq(mlab.numbers_of_basis_sets[mlab.atom_types.index(basis_set.name)],
                   len(basis_set.indices),
                   "\'The numbers of basis sets per atom type\' for basis set " + basis_set.name + " is {0}, but {1} were found")

        for conf_index, atom_index in basis_set.indices:
            if not 1 <= conf_index <= mlab.number_of_configurations:
                raise _error(f"basis set {basis_set.name} references non-existent configration {conf_index}")

            conf = mlab.configurations[conf_index - 1]

            if not 1 <= atom_index <= conf.number_of_atoms:
                raise _error(f"basis set {basis_set.name} references non-existent atom {atom_index} in configration {conf_index}")

            actual_atom = conf.generate_type_lookup()[atom_index - 1]

            if actual_atom != basis_set.name:
                raise _error(f"basis set {basis_set.name} references atom {atom_index}, which is listed as {actual_atom}")


def validate(mlab: MLAB):
    _validate_global(mlab)
    _validate_configurations(mlab)
    _validate_basis_sets(mlab)
