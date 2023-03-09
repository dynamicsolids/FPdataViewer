import re
from collections.abc import Generator
from itertools import chain
from typing import TextIO

from structures import MLAB, MLABBasisSet, MLABConfiguration, Vector, Tensor, MLABConfigurationHeader


def read_blocks(file: TextIO) -> Generator[list[str], None, None]:
    buffer = []

    for line in file:
        if re.match(r"^\s*(=+|-+|\*+)\s*$", line):
            yield buffer
            buffer = []
        else:
            buffer.append(line.strip())

    if len(buffer) != 0:
        yield buffer


# <editor-fold desc="Parsers">
# TODO: Implement error messages (& consolidate?)
def parse_string(data: list[str]) -> str:
    return data[0]


def parse_int(data: list[str]) -> int:
    return int(parse_string(data))


def parse_float(data: list[str]) -> float:
    return float(parse_string(data))


def parse_vector(data: list[str]) -> Vector:
    split = parse_string(data).split()
    return Vector(float(split[0]), float(split[1]), float(split[2]))


def parse_string_list(data: list[str]) -> Generator[str, None, None]:
    yield from chain.from_iterable(map(lambda s: s.split(), data))


def parse_int_list(data: list[str]) -> Generator[int, None, None]:
    yield from map(int, parse_string_list(data))


def parse_float_list(data: list[str]) -> Generator[float, None, None]:
    yield from map(float, parse_string_list(data))


def parse_string_columns(data: list[str]) -> Generator[tuple[str, str], None, None]:
    yield from map(lambda s: tuple(s.split()), data)


def parse_int_columns(data: list[str]) -> Generator[tuple[int, int], None, None]:
    yield from map(lambda s: (int(s[0]), int(s[1])), parse_string_columns(data))


def parse_string_int_columns(data: list[str]) -> Generator[tuple[int, int], None, None]:
    yield from map(lambda s: (s[0], int(s[1])), parse_string_columns(data))


def parse_vector_list(data: list[str]) -> Generator[Vector, None, None]:
    yield from map(lambda s: parse_vector([s]), data)
# </editor-fold>


def read_mlab(path: str) -> MLAB:
    # TODO: Remove asserts & implement error messages
    mlab = MLAB()

    with open(path) as file:
        blocks = read_blocks(file)

        assert(next(blocks) == ["1.0 Version"])

        assert(next(blocks) == ["The number of configurations"])
        mlab.number_of_configurations = parse_int(next(blocks))

        assert(next(blocks) == ["The maximum number of atom type"])
        mlab.max_number_of_atom_types = parse_int(next(blocks))

        assert(next(blocks) == ["The atom types in the data file"])
        mlab.atom_types = list(parse_string_list(next(blocks)))

        assert(next(blocks) == ["The maximum number of atoms per system"])
        mlab.max_number_of_atoms_per_system = parse_int(next(blocks))

        assert(next(blocks) == ["The maximum number of atoms per atom type"])
        mlab.max_number_of_atoms_per_type = parse_int(next(blocks))

        assert(next(blocks) == ["Reference atomic energy (eV)"])
        mlab.reference_energies = list(parse_float_list(next(blocks)))

        assert(next(blocks) == ["Atomic mass"])
        mlab.atomic_masses = list(parse_float_list(next(blocks)))

        assert(next(blocks) == ["The numbers of basis sets per atom type"])
        mlab.numbers_of_basis_sets = list(parse_int_list(next(blocks)))

        last_block = next(blocks)

        mlab.basis_sets = []
        while match := re.match(r"^Basis set for ([a-zA-Z0-9]+)$", parse_string(last_block)):
            bs = MLABBasisSet()
            bs.name = match.group(1)
            bs.indices = list(parse_int_columns(next(blocks)))

            mlab.basis_sets.append(bs)

            last_block = next(blocks)

        mlab.configurations = []
        while match := re.match(r"^Configuration num\.\s+([0-9]+)$", parse_string(last_block)):
            conf = MLABConfiguration()
            conf_header = MLABConfigurationHeader()

            conf.index = int(match.group(1))

            assert(next(blocks) == ["System name"])
            conf_header.name = parse_string(next(blocks))

            assert(next(blocks) == ["The number of atom types"])
            conf_header.number_of_atom_types = parse_int(next(blocks))

            assert(next(blocks) == ["The number of atoms"])
            conf_header.number_of_atoms = parse_int(next(blocks))

            assert(next(blocks) == ["Atom types and atom numbers"])
            conf_header.number_of_atoms_per_type = tuple(parse_string_int_columns(next(blocks)))

            # TODO: Make CTIFOR field optional
            assert(next(blocks) == ["CTIFOR"])
            conf.CTIFOR = parse_float(next(blocks))

            assert(next(blocks) == ["Primitive lattice vectors (ang.)"])
            conf.lattice_vectors = list(parse_vector_list(next(blocks)))

            assert(next(blocks) == ["Atomic positions (ang.)"])
            conf.positions = list(parse_vector_list(next(blocks)))

            assert(next(blocks) == ["Total energy (eV)"])
            conf.energy = parse_float(next(blocks))

            assert(next(blocks) == ["Forces (eV ang.^-1)"])
            conf.forces = list(parse_vector_list(next(blocks)))

            assert(next(blocks) == ["Stress (kbar)"])
            assert(next(blocks) == ["XX YY ZZ"])
            stress_xxyyzz = parse_vector(next(blocks))
            assert(next(blocks) == ["XY YZ ZX"])
            stress_xyyzzx = parse_vector(next(blocks))
            conf.stress = Tensor(stress_xxyyzz.x, stress_xxyyzz.y, stress_xxyyzz.z,
                                 stress_xyyzzx.x, stress_xyyzzx.y, stress_xyyzzx.z)

            conf.header = conf_header
            mlab.configurations.append(conf)

            try:
                last_block = next(blocks)
            except StopIteration:
                break

    return mlab
