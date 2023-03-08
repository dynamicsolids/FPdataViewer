from collections.abc import Generator

from src.structures import MLAB


class ValidationError(Exception):
    message: str
    critical: bool

    def __init__(self, message: str, critical: bool):
        self.message = message
        self.critical = critical


def _validate_header(mlab: MLAB) -> Generator[ValidationError, None, None]:
    # The number of configurations
    report = mlab.number_of_configurations
    actual = len(mlab.configurations)
    if report != actual:
        yield ValidationError(f"\"The number of configurations\" should be {actual} (is {report})", False)

    # The maximum number of atom type
    report = mlab.max_number_of_atom_types
    actual = len(mlab.atom_types)
    if report > actual:
        yield ValidationError(f"\"The maximum number of atom type\" should be at most {actual} (is {report})", False)

    # The maximum number of atoms per system
    report = mlab.max_number_of_atoms_per_system
    actual = max(conf.header.number_of_atoms for conf in mlab.configurations)
    if report != actual:
        yield ValidationError(f"\"The maximum number of atoms per system\" should be {actual} (is {report})", False)

    # The maximum number of atoms per atom type
    report = mlab.max_number_of_atoms_per_type
    actual = max(atom_number for conf in mlab.configurations for _, atom_number in conf.header.number_of_atoms_per_type)
    if report != actual:
        yield ValidationError(f"\"The maximum number of atoms per atom type\" should be {actual} (is {report})", False)


def _validate_atom_types(mlab: MLAB) -> Generator[ValidationError, None, None]:
    # The atom types in the data file
    report = set(mlab.atom_types)
    actual = {atom_type for conf in mlab.configurations for atom_type, _ in conf.header.number_of_atoms_per_type}
    if len(mlab.atom_types) != len(report):
        yield ValidationError("\"The atom types in the data file\" contains duplicate elements", False)

    for atom_type in actual - report:
        yield ValidationError(f"\"The atom types in the data file\" does not contain {atom_type}, seen in structures", False)

    for atom_type in report - actual:
        yield ValidationError(f"\"The atom types in the data file\" contains {atom_type}, not seen in any structure", False)

    # Reference atomic energy (eV)
    report = len(mlab.atom_types)
    actual = len(mlab.reference_energies)
    if report != actual:
        yield ValidationError(f"\"Reference atomic energy\" should contain {report} entries (is {actual})", False)

    # Atomic mass
    report = len(mlab.atom_types)
    actual = len(mlab.atomic_masses)
    if report != actual:
        yield ValidationError(f"\"Atomic mass\" should contain {report} entries (is {actual})", False)

    # The numbers of basis sets per atom type
    report = len(mlab.atom_types)
    actual = len(mlab.numbers_of_basis_sets)
    if report != actual:
        yield ValidationError(f"\"The numbers of basis sets per atom type\" should contain {report} entries (is {actual})", False)

    # Basis sets
    report = set(mlab.atom_types)
    actual = {basis_set.name for basis_set in mlab.basis_sets}
    for atom_type in report - actual:
        yield ValidationError(f"\"The atom types in the data file\" contains {atom_type}, but lacks basis set", False)

    for atom_type in actual - report:
        yield ValidationError(f"\"The atom types in the data file\" does not contain {atom_type}, but has basis set", False)


def _validate_basis_sets(mlab: MLAB) -> Generator[ValidationError, None, None]:
    pass


def validate_mlab(mlab: MLAB) -> Generator[ValidationError, None, None]:
    yield from _validate_header(mlab)

    yield from _validate_atom_types(mlab)

    #yield from _validate_basis_sets(mlab)
