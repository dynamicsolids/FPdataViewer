import math
from dataclasses import dataclass
from itertools import chain


@dataclass(frozen=True, slots=True)
class Vector:
    x: float
    y: float
    z: float

    def get_length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    @staticmethod
    def get_distance(a: "Vector", b: "Vector") -> float:
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)


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


@dataclass(init=False, slots=True)
class MLABBasisSet:
    name: str
    indices: list[tuple[int, int]]


@dataclass(init=False, slots=True, unsafe_hash=True)
class MLABConfigurationHeader:
    name: str
    number_of_atom_types: int
    number_of_atoms: int
    number_of_atoms_per_type: tuple[tuple[str, int]]

    def generate_type_lookup(self) -> tuple[str]:
        table = [[type] * number for type, number in self.number_of_atoms_per_type]
        return tuple(chain.from_iterable(table))


@dataclass(init=False, slots=True)
class MLABConfiguration:
    index: int

    header: MLABConfigurationHeader

    CTIFOR: int | None
    lattice_vectors: list[Vector]
    positions: list[Vector]
    energy: float
    forces: list[Vector]
    stress: Tensor


@dataclass(init=False, slots=True)
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


@dataclass(slots=True)
class MLABGroup:
    mlab: MLAB
    header: MLABConfigurationHeader
    configurations: list[MLABConfiguration]
