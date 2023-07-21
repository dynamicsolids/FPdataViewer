import numpy as np
from numpy.typing import ArrayLike

from internal.structures import MLABSection


def calculate_rdf(section: MLABSection,
                  center: set[str],
                  to: set[str],
                  rmin: float,
                  rmax: float,
                  number_bins: int,
                  structure_count: int) -> tuple[ArrayLike, ArrayLike]:
    # TODO: Handle invalid atom types
    counts = np.zeros(number_bins)
    # np.histogram_bin_edges()

    type_lookup = section.common_header.generate_type_lookup()

    center_indices = [i for i in range(section.common_header.number_of_atoms) if type_lookup[i] in center]
    to_indices = [i for i in range(section.common_header.number_of_atoms) if type_lookup[i] in to]

    pairs = np.array([(center_index, to_index)
                      for center_index in center_indices
                      for to_index in to_indices
                      if center_index != to_index])

    offset_matrix = np.array([[ 0,  0, 0], [ 0,  0, -1], [ 0,  0, 1],
                              [ 0, -1, 0], [ 0, -1, -1], [ 0, -1, 1],
                              [ 0,  1, 0], [ 0,  1, -1], [ 0,  1, 1],
                              [-1,  0, 0], [-1,  0, -1], [-1,  0, 1],
                              [-1, -1, 0], [-1, -1, -1], [-1, -1, 1],
                              [-1,  1, 0], [-1,  1, -1], [-1,  1, 1],
                              [ 1,  0, 0], [ 1,  0, -1], [ 1,  0, 1],
                              [ 1, -1, 0], [ 1, -1, -1], [ 1, -1, 1],
                              [ 1,  1, 0], [ 1,  1, -1], [ 1,  1, 1]])

    source = np.random.choice(section.configurations, structure_count) if structure_count < len(section.configurations) else section.configurations
    for conf in source:
        offsets = offset_matrix @ conf.lattice_vectors

        for center_index, to_index in pairs:
            for offset in offsets:
                # distance = np.linalg.norm(conf.positions[center_index] - conf.positions[to_index] - offset)
                difference = conf.positions[center_index] - conf.positions[to_index] - offset
                distance = np.sqrt(difference[0]**2 + difference[1]**2 + difference[2]**2)

                if rmin <= distance < rmax:
                    counts[int((distance - rmin) / (rmax - rmin) * number_bins)] += 1

    counts /= len(source) * len(center_indices)

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