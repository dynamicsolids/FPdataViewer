import numpy as np
from numpy.typing import ArrayLike

from internal.structures import MLABGroup


def calculate_radial_distribution(group: MLABGroup, center: set[str], to: set[str], rmin: float, rmax: float, number_bins: int, number_structures: int) -> tuple[ArrayLike, ArrayLike]:
    bins = np.zeros(number_bins)

    type_lookup = group.header.generate_type_lookup()

    center_indices = [i for i in range(group.header.number_of_atoms) if type_lookup[i] in center]
    to_indices = [i for i in range(group.header.number_of_atoms) if type_lookup[i] in to]

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

    source = np.random.choice(group.configurations, number_structures) if number_structures < len(group.configurations) else group.configurations
    for conf in source:
        offsets = offset_matrix @ conf.lattice_vectors

        for center_index, to_index in pairs:
            for offset in offsets:
                # distance = np.linalg.norm(conf.positions[center_index] - conf.positions[to_index] - offset)
                difference = conf.positions[center_index] - conf.positions[to_index] - offset
                distance = np.sqrt(difference[0]**2 + difference[1]**2 + difference[2]**2)

                if rmin <= distance <= rmax:
                    bins[int((distance - rmin) / (rmax - rmin) * number_bins)] += 1

    bins /= len(source) * len(center_indices)

    radii = np.linspace(rmin, rmax, number_bins + 1)
    for i in range(number_bins):
        inner_radius = radii[i]
        outer_radius = radii[i + 1]
        volume = 4 / 3 * np.pi * (outer_radius**3 - inner_radius**3)
        bins[i] /= volume

    total_volume = np.linalg.det(group.configurations[0].lattice_vectors)
    density = len(to_indices) / total_volume
    bins /= density

    return radii, np.insert(bins, 0, bins[0])
