import numpy as np
from numba import njit
from numpy.typing import ArrayLike

from mlab.mlab import MLABSection
from src.internal.config import get_config


def calculate_rdfs(section: MLABSection) -> dict[tuple[str, str], tuple[ArrayLike, ArrayLike]]:
    rmin = get_config()["rdf"]["r_min"]
    rmax = get_config()["rdf"]["r_max"]
    bin_number = get_config()["rdf"]["bins"]
    structures = get_config()["rdf"]["structures"]

    if isinstance(structures, float) and 0. <= structures <= 1.:
        structures = int(structures * len(section.configurations))

    pairs = _get_pairs_from_config(section)
    rdfs = {}

    for center, to in pairs:
        print(f"\rcalculating radial distribution function for {center}-{to} ... ", end="")

        bins, data = _calculate_rdf(section, {center}, {to}, rmin, rmax, bin_number, structures)
        rdfs[(center, to)] = (bins, data)

    return rdfs


def _get_pairs_from_config(section: MLABSection) -> list[tuple[str, str]]:
    atoms = [atom for atom, _ in section.number_of_atoms_per_type]

    all_pairs = [(atoms[i], atoms[j]) for i in range(len(atoms)) for j in range(i, len(atoms))]

    skipped_pairs = [pair_str.split("-") for pair_str in get_config()["rdf"]["skip_pairs"]]

    return [(atom1, atom2)
            for atom1, atom2 in all_pairs
            if (atom1, atom2) not in skipped_pairs and (atom2, atom1) not in skipped_pairs]


def _calculate_rdf(section: MLABSection,
                   center: set[str],
                   to: set[str],
                   rmin: float,
                   rmax: float,
                   number_bins: int,
                   structure_count: int) -> tuple[ArrayLike, ArrayLike]:
    # TODO: handle invalid atom types
    counts = np.zeros(number_bins)

    type_lookup = section.header.generate_type_lookup()

    center_indices = [i for i in range(section.header.number_of_atoms) if type_lookup[i] in center]
    to_indices = [i for i in range(section.header.number_of_atoms) if type_lookup[i] in to]

    pairs = np.array([(center_index, to_index)
                      for center_index in center_indices
                      for to_index in to_indices
                      if center_index != to_index])

    selected_configurations = np.random.choice(section.configurations, structure_count) if 1 <= structure_count < len(section.configurations) else section.configurations

    # TODO: very memory inefficient. we have to copy all positions (basically all data) into a contiguous piece of memory, because numba cannot deal with our MLABSection type.
    contiguous_positions = np.array([conf.positions for conf in selected_configurations])
    contiguous_lattice_vectors = np.array([conf.lattice_vectors for conf in selected_configurations])

    _calculate_rdf_bins(contiguous_positions,
                        contiguous_lattice_vectors,
                        pairs,
                        rmin,
                        rmax,
                        number_bins,
                        counts)

    counts /= len(selected_configurations) * len(center_indices)

    bins = np.linspace(rmin, rmax, number_bins + 1)
    for i in range(number_bins):
        inner_radius = bins[i]
        outer_radius = bins[i + 1]
        volume = 4 / 3 * np.pi * (outer_radius**3 - inner_radius**3)
        counts[i] /= volume

    total_volume = np.linalg.det(section.configurations[0].lattice_vectors)
    density = len(to_indices) / total_volume
    counts /= density

    return counts, bins

@njit
def _calculate_rdf_bins(positions,
                        lattice_vectors,
                        pairs,
                        rmin: float,
                        rmax: float,
                        number_bins: int,
                        counts):
    offset_matrix = np.array([[x, y, z]
                              for x in [-1, 0, 1]
                              for y in [-1, 0, 1]
                              for z in [-1, 0, 1]], dtype=np.float64)

    for i in range(len(positions)):
        offsets = offset_matrix @ lattice_vectors[i]

        for offset in offsets:
            for center_index, to_index in pairs:
                dx = positions[i, center_index, 0] - positions[i, to_index, 0] - offset[0]
                dy = positions[i, center_index, 1] - positions[i, to_index, 1] - offset[1]
                dz = positions[i, center_index, 2] - positions[i, to_index, 2] - offset[2]

                distance = dx ** 2 + dy ** 2 + dz ** 2

                if rmin ** 2 <= distance < rmax ** 2:
                    distance = np.sqrt(distance)

                    bin = int((distance - rmin) / (rmax - rmin) * number_bins)
                    counts[bin] += 1
