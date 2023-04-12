from dataclasses import dataclass
from itertools import chain

from numpy.typing import ArrayLike


@dataclass(frozen=True, slots=True)
class Tensor:
    xx: float
    yy: float
    zz: float
    xy: float
    yz: float
    zx: float

    def get_mechanical_pressure(self):
        return (self.xx + self.yy + self.zz) / 3


@dataclass(frozen=True, slots=True)
class MLABBasisSet:
    name: str
    indices: ArrayLike


@dataclass(frozen=True, slots=True, kw_only=True, unsafe_hash=True)
class MLABConfigurationHeader:
    name: str
    number_of_atom_types: int
    number_of_atoms: int
    number_of_atoms_per_type: tuple[tuple[str, int], ...]

    def generate_type_lookup(self) -> tuple[str, ...]:
        table = [[type] * number for type, number in self.number_of_atoms_per_type]
        return tuple(chain.from_iterable(table))


@dataclass(frozen=True, slots=True, kw_only=True)
class MLABConfiguration:
    index: int

    header: MLABConfigurationHeader

    ctifor: float | None
    lattice_vectors: ArrayLike
    positions: ArrayLike
    energy: float
    forces: ArrayLike
    stress: Tensor


@dataclass(frozen=True, slots=True, kw_only=True)
class MLAB:
    number_of_configurations: int
    max_number_of_atom_types: int
    max_number_of_atoms_per_system: int
    max_number_of_atoms_per_type: int

    atom_types: list[str]
    reference_energies: list[float]
    atomic_masses: list[float]
    numbers_of_basis_sets: list[int]

    basis_sets: list[MLABBasisSet]

    configurations: list[MLABConfiguration]


@dataclass(frozen=True, slots=True, kw_only=True)
class MLABGroup:
    mlab: MLAB
    header: MLABConfigurationHeader
    configurations: list[MLABConfiguration]


@dataclass(frozen=True, slots=True, kw_only=True)
class MLABGroupAnalysis:
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class MLABAnalysis:
    hash: str
    groups: list[MLABGroupAnalysis]
