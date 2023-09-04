import re
from collections import defaultdict
from collections.abc import Iterator
from typing import TextIO

import numpy as np
from numpy.typing import ArrayLike

from mlab_tools.structures import MLAB, MLABBasisSet, MLABConfiguration, StressTensor, MLABConfigurationHeader, MLABSection


class MLABParser:
    _re_divider = re.compile(r"^\s*(=+|-+|\*+)\s*$")
    _re_basis_set = re.compile(r"^Basis set for ([a-zA-Z0-9]+)$")
    _re_configuration = re.compile(r"^Configuration num\.\s+([0-9]+)$")

    def __init__(self, file: TextIO):
        self._file = file
        self._header_buffer = None
        self._throw_on_end_of_file = True
        self._end_of_file = False

    def _readline(self) -> str:
        line = self._file.readline().strip()
        if line == "":
            raise Exception()
        else:
            return line

    def _divider_exists(self) -> bool:
        line = self._file.readline()

        if line == "":
            self._end_of_file = True

            if self._throw_on_end_of_file:
                raise Exception
            else:
                return True

        return self._re_divider.fullmatch(line) is not None

    def _readlines(self) -> Iterator[str]:
        while True:
            line = self._file.readline()

            if line == "":
                self._end_of_file = True

                if self._throw_on_end_of_file:
                    raise Exception()
                else:
                    break

            if self._re_divider.fullmatch(line):
                break

            yield line

    # <editor-fold desc="Parsers">

    def _read_string(self) -> str:
        res = self._readline()

        if not self._divider_exists():
            raise Exception()

        return res

    def _read_int(self) -> int:
        return int(self._read_string())

    def _read_float(self) -> float:
        return float(self._read_string())

    def _read_vector(self) -> tuple[float, float, float]:
        split = self._read_string().split()
        return float(split[0]), float(split[1]), float(split[2])

    def _read_basis_set(self, size: int) -> ArrayLike:
        res = np.empty((size, 2), dtype=int)

        for i in range(size):
            split = self._readline().split()
            res[i, 0] = int(split[0])
            res[i, 1] = int(split[1])

        if not self._divider_exists():
            raise Exception()

        return res

    def _read_atoms(self, size: int) -> Iterator[tuple[str, int]]:
        for i in range(size):
            split = self._readline().split()

            yield split[0], int(split[1])

        if not self._divider_exists():
            raise Exception()

    def _read_vector_list(self, size: int) -> ArrayLike:
        # res = np.empty((size, 3), dtype=float)
        #
        # for i in range(size):
        #     split = self._readline().split()
        #     res[i, 0] = float(split[0])
        #     res[i, 1] = float(split[1])
        #     res[i, 2] = float(split[2])
        res = np.loadtxt(self._file, ndmin=2, max_rows=size)

        if not self._divider_exists():
            raise Exception()

        return res

    def _read_string_list(self) -> Iterator[str]:
        for line in self._readlines():
            yield from line.split()

    def _read_int_list(self) -> Iterator[int]:
        for s in self._read_string_list():
            yield int(s)

    def _read_float_list(self) -> Iterator[float]:
        for s in self._read_string_list():
            yield float(s)

    def _read_header(self, expected: str):
        if self._header_buffer == expected:
            self._header_buffer = None
        elif self._read_string() != expected:
            raise Exception()

    def _read_optional_header(self, expected: str) -> bool:
        header = self._read_string()
        present = header == expected

        if not present:
            self._header_buffer = header

        return present

    # </editor-fold>

    def load(self) -> MLAB:
        self._read_header("1.0 Version")

        self._read_header("The number of configurations")
        number_of_configurations = self._read_int()

        self._read_header("The maximum number of atom type")
        max_number_of_atom_types = self._read_int()

        self._read_header("The atom types in the data file")
        atom_types = list(self._read_string_list())

        self._read_header("The maximum number of atoms per system")
        max_number_of_atoms_per_system = self._read_int()

        self._read_header("The maximum number of atoms per atom type")
        max_number_of_atoms_per_type = self._read_int()

        self._read_header("Reference atomic energy (eV)")
        reference_energies = list(self._read_float_list())

        self._read_header("Atomic mass")
        atomic_masses = list(self._read_float_list())

        self._read_header("The numbers of basis sets per atom type")
        numbers_of_basis_sets = list(self._read_int_list())

        basis_sets = []
        last_block = self._read_string()
        while match := self._re_basis_set.fullmatch(last_block):
            name = match.group(1)

            number_of_elements = numbers_of_basis_sets[atom_types.index(name)]

            indices = self._read_basis_set(number_of_elements)

            basis_sets.append(MLABBasisSet(name=name,
                                           indices=indices))

            last_block = self._read_string()

        header_pool = {}
        configurations = []
        while match := self._re_configuration.fullmatch(last_block):
            index = int(match.group(1))

            self._read_header("System name")
            name = self._read_string()

            self._read_header("The number of atom types")
            number_of_atom_types = self._read_int()

            self._read_header("The number of atoms")
            number_of_atoms = self._read_int()

            self._read_header("Atom types and atom numbers")
            number_of_atoms_per_type = tuple(self._read_atoms(number_of_atom_types))

            reference_header = MLABConfigurationHeader(name=name,
                                                       number_of_atom_types=number_of_atom_types,
                                                       number_of_atoms=number_of_atoms,
                                                       number_of_atoms_per_type=number_of_atoms_per_type)
            header_obj = header_pool.get(reference_header)
            if header_obj is None:
                header_obj = reference_header
                header_pool[reference_header] = reference_header

            if self._read_optional_header("CTIFOR"):
                ctifor = self._read_float()
            else:
                ctifor = None

            self._read_header("Primitive lattice vectors (ang.)")
            lattice_vectors = self._read_vector_list(3)

            self._read_header("Atomic positions (ang.)")
            positions = self._read_vector_list(number_of_atoms)

            self._read_header("Total energy (eV)")
            energy = self._read_float()

            self._read_header("Forces (eV ang.^-1)")
            forces = self._read_vector_list(number_of_atoms)

            self._read_header("Stress (kbar)")
            self._read_header("XX YY ZZ")
            xx, yy, zz = self._read_vector()
            self._read_header("XY YZ ZX")
            self._throw_on_end_of_file = False
            xy, yz, zx = self._read_vector()
            self._throw_on_end_of_file = True

            stress = StressTensor(xx, yy, zz, xy, yz, zx)

            configurations.append(MLABConfiguration(index=index,
                                                    header=header_obj,
                                                    ctifor=ctifor,
                                                    lattice_vectors=lattice_vectors,
                                                    positions=positions,
                                                    energy=energy,
                                                    forces=forces,
                                                    stress=stress))

            if self._end_of_file:
                break

            last_block = self._read_string()

        return MLAB(number_of_configurations=number_of_configurations,
                    max_number_of_atom_types=max_number_of_atom_types,
                    atom_types=atom_types,
                    max_number_of_atoms_per_system=max_number_of_atoms_per_system,
                    max_number_of_atoms_per_type=max_number_of_atoms_per_type,
                    reference_energies=reference_energies,
                    atomic_masses=atomic_masses,
                    numbers_of_basis_sets=numbers_of_basis_sets,
                    basis_sets=basis_sets,
                    configurations=configurations)

def load(file: TextIO) -> MLAB:
    return MLABParser(file).load()


def split(mlab: MLAB) -> list[MLABSection]:
    sections = defaultdict(list)

    for conf in mlab.configurations:
        sections[conf.header].append(conf)

    return [MLABSection(configurations=confs, source=mlab, common_header=header) for header, confs in sections.items()]
