from __future__ import annotations

import re
from collections import defaultdict
from typing import TextIO, Optional

import numpy as np
from numpy.typing import ArrayLike

from fpdataviewer.mlab.mlab import MLAB, MLABBasisSet, MLABConfiguration, StressTensor, MLABConfigurationHeader, MLABSection

_re_divider = re.compile(r"^\s*(=+|-+|\*+)\s*$")
_re_basis_set = re.compile(r"^Basis set for ([a-zA-Z0-9]+)$")
_re_configuration = re.compile(r"^Configuration num\.\s+([0-9]+)$")


class ParserException(Exception):
    def __init__(self, message):
        super().__init__(message)


class MLABReader:
    def __init__(self, stream: TextIO):
        self.stream = stream

        self.line_counter = 1
        self.buffer_start_line = 1
        self.buffer_end_line = 1

        self.buffer = []
        self.eof = False

        self.keep_buffer = False

    def advance(self) -> None:
        if self.keep_buffer:
            self.keep_buffer = False
            return

        self.buffer.clear()

        self.buffer_start_line = self.line_counter
        self.buffer_end_line = self.line_counter

        while True:
            line = self.stream.readline()
            self.line_counter += 1

            if _re_divider.fullmatch(line):
                self.eof = False
                break
            elif line == "":
                self.eof = True
                break
            else:
                stripped = line.strip()
                if stripped != "":
                    self.buffer.append(stripped)

            self.buffer_end_line = self.line_counter

        if len(self.buffer) == 0 and self.eof:
            raise ParserException("unexpected end of file")

    def error(self, message: str) -> ParserException:
        return ParserException(f"on lines {self.buffer_start_line}-{self.buffer_end_line}: {message}, found {repr(''.join(self.buffer))}")

    def consume_sl_string(self) -> str:
        self.advance()

        if len(self.buffer) == 1:
            return self.buffer[0]
        else:
            raise self.error("expected single line")

    def consume_sl_int(self) -> int:
        self.advance()

        if len(self.buffer) == 1:
            try:
                return int(self.buffer[0])
            except ValueError:
                raise self.error("expected integer")
        else:
            raise self.error("expected single line")

    def consume_sl_float(self) -> float:
        self.advance()

        if len(self.buffer) == 1:
            try:
                return float(self.buffer[0])
            except ValueError:
                raise self.error("expected decimal number")
        else:
            raise self.error("expected single line")

    def consume_sl_vector(self) -> tuple[float, float, float]:
        self.advance()

        if len(self.buffer) == 1:
            try:
                split = self.buffer[0].split()
                return float(split[0]), float(split[1]), float(split[2])
            except ValueError:
                raise self.error("expected vector of decimal numbers")
        else:
            raise self.error("expected single line")

    def consume_ml_array(self) -> ArrayLike:
        self.advance()

        return np.loadtxt(self.buffer)

    def consume_ml_strings(self) -> list[str]:
        self.advance()

        return [entry for line in self.buffer for entry in line.split()]

    def consume_ml_ints(self) -> list[int]:
        self.advance()

        try:
            return [int(entry) for line in self.buffer for entry in line.split()]
        except ValueError:
            raise self.error("expected list of integers")

    def consume_ml_floats(self) -> list[float]:
        self.advance()

        try:
            return [float(entry) for line in self.buffer for entry in line.split()]
        except ValueError:
            raise self.error("expected list of decimal numbers")

    def consume_ml_basis(self) -> ArrayLike:
        self.advance()

        return np.loadtxt(self.buffer, dtype=int)

    def consume_ml_atoms(self) -> list[tuple[str, int]]:
        self.advance()

        try:
            res = []

            for line in self.buffer:
                split = line.split()
                res.append((split[0], int(split[1])))

            return res
        except ValueError:
            raise self.error("expected list of string-integer tuples")

    def consume_header(self, expected_header: str) -> None:
        self.advance()

        if len(self.buffer) != 1 or self.buffer[0] != expected_header:
            raise self.error(f"expected to find {repr(expected_header)}")

    def peek_header(self, expected_header: str) -> bool:
        self.advance()

        found_header = len(self.buffer) == 1 and self.buffer[0] == expected_header

        self.keep_buffer = not found_header

        return found_header

    def consume_regex(self, pattern: re.Pattern[str]) -> re.Match:
        self.advance()

        if len(self.buffer) == 1:
            match = pattern.fullmatch(self.buffer[0])

            if not match:
                raise self.error(f"expected pattern {repr(pattern.pattern)}")

            return match
        else:
            raise self.error("expected single line")

    def peek_regex(self, pattern: re.Pattern[str]) -> Optional[re.Match]:
        self.advance()

        if len(self.buffer) == 1:
            match = pattern.fullmatch(self.buffer[0])
        else:
            match = None

        if not match:
            self.keep_buffer = True

        return match


def load(stream: TextIO) -> MLAB:
    reader = MLABReader(stream)

    reader.advance() # Initial comment, usually either empty or "1.0 Version"

    reader.consume_header("The number of configurations")
    number_of_configurations = reader.consume_sl_int()

    reader.consume_header("The maximum number of atom type")
    max_number_of_atom_types = reader.consume_sl_int()

    reader.consume_header("The atom types in the data file")
    atom_types = reader.consume_ml_strings()

    reader.consume_header("The maximum number of atoms per system")
    max_number_of_atoms_per_system = reader.consume_sl_int()

    reader.consume_header("The maximum number of atoms per atom type")
    max_number_of_atoms_per_type = reader.consume_sl_int()

    reader.consume_header("Reference atomic energy (eV)")
    reference_energies = reader.consume_ml_floats()

    reader.consume_header("Atomic mass")
    atomic_masses = reader.consume_ml_floats()

    reader.consume_header("The numbers of basis sets per atom type")
    numbers_of_basis_sets = reader.consume_ml_ints()

    basis_sets = []
    while name_match := reader.peek_regex(_re_basis_set):
        name = name_match.group(1)

        indices = reader.consume_ml_basis()

        basis_sets.append(MLABBasisSet(name=name,
                                       indices=indices))

    header_pool = {}
    configurations = []
    while index_match := reader.consume_regex(_re_configuration):
        try:
            index = int(index_match.group(1))
        except ValueError:
            raise reader.error("invalid configuration number")

        reader.consume_header("System name")
        name = reader.consume_sl_string()

        reader.consume_header("The number of atom types")
        number_of_atom_types = reader.consume_sl_int()

        reader.consume_header("The number of atoms")
        number_of_atoms = reader.consume_sl_int()

        reader.consume_header("Atom types and atom numbers")
        number_of_atoms_per_type = tuple(reader.consume_ml_atoms())

        header_candidate = MLABConfigurationHeader(name=name,
                                                   number_of_atom_types=number_of_atom_types,
                                                   number_of_atoms=number_of_atoms,
                                                   number_of_atoms_per_type=number_of_atoms_per_type)

        header = header_pool.get(header_candidate)
        if header is None:
            header = header_candidate
            header_pool[header_candidate] = header_candidate

        if reader.peek_header("CTIFOR"):
            ctifor = reader.consume_sl_float()
        else:
            ctifor = None

        reader.consume_header("Primitive lattice vectors (ang.)")
        lattice_vectors = reader.consume_ml_array()

        reader.consume_header("Atomic positions (ang.)")
        positions = reader.consume_ml_array()

        reader.consume_header("Total energy (eV)")
        energy = reader.consume_sl_float()

        reader.consume_header("Forces (eV ang.^-1)")
        forces = reader.consume_ml_array()

        reader.consume_header("Stress (kbar)")
        reader.consume_header("XX YY ZZ")
        xx, yy, zz = reader.consume_sl_vector()
        reader.consume_header("XY YZ ZX")
        xy, yz, zx = reader.consume_sl_vector()

        stress = StressTensor(xx, yy, zz, xy, yz, zx)

        if not reader.eof and reader.peek_header("Charges (e)"):
            charges = reader.consume_ml_array()
        else:
            charges = None

        configurations.append(MLABConfiguration(index=index,
                                                header=header,
                                                ctifor=ctifor,
                                                lattice_vectors=lattice_vectors,
                                                positions=positions,
                                                energy=energy,
                                                forces=forces,
                                                stress=stress,
                                                charges=charges))

        if reader.eof:
            break

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


def write(stream: TextIO, mlab: MLAB) -> None:
    #from fortranformat import FortranRecordWriter
    #format = FortranRecordWriter("(5X, 3EN24.13)")
    #stream.write(format.write([np.sqrt(2), -np.sqrt(2), np.sqrt(5)]))

    star_divider = "*" * 50
    line_divider = "-" * 50
    conf_divider = "=" * 50

    def split_over_lines(l: list, n: int) -> str:
        return "\n".join(" ".join(map(str, l[i:i+n])) for i in range(0, len(l), n))

    def writelns(a: list) -> None:
        stream.write("\n".join(map(str, a)))
        stream.write("\n")

    writelns([
        "1.0 Version",
        star_divider, "The number of configurations", line_divider,
        mlab.number_of_configurations,
        star_divider, "The maximum number of atom type", line_divider,
        mlab.max_number_of_atom_types,
        star_divider, "The atom types in the data file", line_divider,
        split_over_lines(mlab.atom_types, 3),
        star_divider, "The maximum number of atoms per system", line_divider,
        mlab.max_number_of_atoms_per_system,
        star_divider, "The maximum number of atoms per atom type", line_divider,
        mlab.max_number_of_atoms_per_type,
        star_divider, "Reference atomic energy (eV)", line_divider,
        split_over_lines(mlab.reference_energies, 3),
        star_divider, "Atomic mass", line_divider,
        split_over_lines(mlab.atomic_masses, 3),
        star_divider, "The numbers of basis sets per atom type", line_divider,
        split_over_lines(mlab.numbers_of_basis_sets, 3),
    ])

    for set in mlab.basis_sets:
        writelns([
            star_divider, f"Basis set for {set.name}", line_divider,
            "\n".join(f"{ic} {ia}" for ic, ia in set.indices),
        ])

    for conf in mlab.configurations:
        writelns([
            star_divider, f"Configuration num. {conf.index}",
            conf_divider, "System name", line_divider,
            conf.name,
            conf_divider, "The number of atom types", line_divider,
            conf.number_of_atom_types,
            conf_divider, "The number of atoms", line_divider,
            conf.number_of_atoms,
            star_divider, "Atom types and atom numbers", line_divider,
            "\n".join(f"{name} {number}" for name, number in conf.number_of_atoms_per_type),
        ])

        if conf.ctifor is not None:
            writelns([
                conf_divider, "CTIFOR", line_divider,
                conf.ctifor,
            ])

        writelns([
            conf_divider, "Primitive lattice vectors (ang.)", line_divider,
            "\n".join(f"{x} {y} {z}" for x, y, z in conf.lattice_vectors),
            conf_divider, "Atomic positions (ang.)", line_divider,
            "\n".join(f"{x} {y} {z}" for x, y, z in conf.positions),
            conf_divider, "Total energy (eV)", line_divider,
            conf.energy,
            conf_divider, "Forces (eV ang.^-1)", line_divider,
            "\n".join(f"{x} {y} {z}" for x, y, z in conf.forces),
            conf_divider, "Stress (kbar)",
            line_divider, "XX YY ZZ", line_divider,
            f"{conf.stress.xx} {conf.stress.yy} {conf.stress.zz}",
            line_divider, "XY YZ ZX", line_divider,
            f"{conf.stress.xy} {conf.stress.yz} {conf.stress.zx}",
        ])


def split(mlab: MLAB) -> list[MLABSection]:
    sections = defaultdict(list)

    for conf in mlab.configurations:
        sections[conf.header].append(conf)

    return [MLABSection(configurations=confs, source=mlab, header=header) for header, confs in sections.items()]
