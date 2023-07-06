import numpy as np
from dscribe.descriptors import SOAP
from numpy.typing import ArrayLike
from sklearn.decomposition import PCA

from internal.adapters.ase_adapter import section_to_atoms
from internal.config import get_config
from internal.structures import MLABSection, MLABSectionStats


def _get_pairs_from_config(section: MLABSection, pairs_str: str | list[str]) -> list[tuple[str, str]]:
    # TODO: Handle invalid input (or move this handling to other function?)
    atoms = [atom for atom, _ in section.common_header.number_of_atoms_per_type]

    if pairs_str == "same":
        return list(zip(atoms, atoms))
    else:
        pairs = set()

        for pair_str in pairs_str:
            atom1, atom2 = pair_str.split("-")

            if atom1 in atoms and atom2 in atoms:
                pairs.add((atom1, atom2))

        return list(pairs)


def calculate_radial_distribution(section: MLABSection, center: set[str], to: set[str], rmin: float, rmax: float, number_bins: int, structure_count: int) -> tuple[ArrayLike, ArrayLike]:
    # TODO: Handle invalid atom types
    bins = np.zeros(number_bins)

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

                if rmin <= distance <= rmax:
                    bins[int((distance - rmin) / (rmax - rmin) * number_bins)] += 1

    bins /= len(source) * len(center_indices)

    radii = np.linspace(rmin, rmax, number_bins + 1)
    for i in range(number_bins):
        inner_radius = radii[i]
        outer_radius = radii[i + 1]
        volume = 4 / 3 * np.pi * (outer_radius**3 - inner_radius**3)
        bins[i] /= volume

    total_volume = np.linalg.det(section.configurations[0].lattice_vectors)
    density = len(to_indices) / total_volume
    bins /= density

    return radii, np.insert(bins, 0, bins[0])


def calculate_radial_distributions(section: MLABSection) -> dict[str, tuple[ArrayLike, ArrayLike]]:
    rmin = get_config()["rdf"]["r_min"]
    rmax = get_config()["rdf"]["r_max"]
    bin_number = get_config()["rdf"]["bins"]
    structures = get_config()["rdf"]["structures"]

    if isinstance(structures, float) and 0. <= structures <= 1.:
        structures = int(structures * len(section.configurations))

    pairs = _get_pairs_from_config(section, get_config()["rdf"]["pairs"])
    rdfs = {}

    for center, to in pairs:
        print(f"Calculating radial distribution function for {center}-{to}")

        bins, data = calculate_radial_distribution(section, {center}, {to}, rmin, rmax, bin_number, structures)
        rdfs[f"{center}-{to}"] = (bins, data)

    return rdfs


def calculate_descriptors(section: MLABSection) -> dict[str, ArrayLike]:
    section_ase = section_to_atoms(section)

    soap = SOAP(
        species=[type for type, _ in section.number_of_atoms_per_type],
        periodic=True,
        r_cut=5,
        n_max=8,
        l_max=8,
        average="off",
        sparse=False,
        dtype="float32",
    )

    descriptors_per_type = {}

    for type, _ in section.number_of_atoms_per_type:
        print(f"Calculating feature vectors for {type}")
        centers = [i for i, t in enumerate(section.generate_type_lookup()) if t == type]

        feature_vectors = soap.create(section_ase, centers=[centers for _ in section_ase], n_jobs=-1)
        feature_vectors = feature_vectors.reshape(-1, feature_vectors.shape[-1])

        pca = PCA(n_components=2, copy=False)

        feature_vectors = pca.fit_transform(feature_vectors)

        descriptors_per_type[type] = feature_vectors

    return descriptors_per_type


def get_stats(section: MLABSection) -> MLABSectionStats:
    return MLABSectionStats(
        rdfs=calculate_radial_distributions(section),
        descriptors=calculate_descriptors(section),
    )
