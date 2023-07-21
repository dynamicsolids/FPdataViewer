from dataclasses import dataclass
from operator import attrgetter

import numpy as np
import pandas as pd
from PySide6.QtGui import QImage
from dscribe.descriptors import SOAP
from numpy.typing import ArrayLike
from sklearn.decomposition import PCA

from internal import rendering
from internal.adapters.ase_adapter import section_to_atoms
from internal.config import get_config
from internal.rdf import calculate_rdf
from internal.structures import MLABSection, MLABConfiguration


def _get_pairs_from_config(section: MLABSection, pairs_str: str | list[str]) -> list[tuple[str, str]]:
    atoms = [atom for atom, _ in section.number_of_atoms_per_type]

    if pairs_str == "auto":
        return list(zip(atoms, atoms))
    else:
        pairs = set()

        for pair_str in pairs_str:
            atom1, atom2 = pair_str.split("-")

            if atom1 in atoms and atom2 in atoms:
                pairs.add((atom1, atom2))

        return list(pairs)


def _calculate_rdfs(section: MLABSection) -> dict[str, tuple[ArrayLike, ArrayLike]]:
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

        bins, data = calculate_rdf(section, {center}, {to}, rmin, rmax, bin_number, structures)
        rdfs[f"{center}-{to}"] = (bins, data)

    return rdfs


def _calculate_descriptors(section: MLABSection) -> dict[str, pd.DataFrame]:
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
        feature_vectors = feature_vectors.reshape((-1, feature_vectors.shape[-1]))

        pca = PCA(n_components=2, copy=False)

        feature_vectors = pca.fit_transform(feature_vectors)

        all_basis_sets = [(i, j) for basis_set in section.source.basis_sets for i, j in basis_set.indices]

        energies = [conf.energy for conf in section.configurations for _ in centers]
        is_basis = [(i, j) in all_basis_sets for i, conf in enumerate(section.configurations) for j in centers]

        descriptors = pd.DataFrame({
            "pc_1": feature_vectors[:, 0],
            "pc_2": feature_vectors[:, 1],
            "energy": energies,
            "basis": is_basis,
        })

        descriptors_per_type[type] = descriptors.sample(frac=1).reset_index(drop=True)

    return descriptors_per_type


def _calculate_general(section: MLABSection) -> pd.DataFrame:
    def conf_to_dict(conf: MLABConfiguration) -> dict[str, float]:
        return {
            "energy": conf.energy,
            "pressure": -(conf.stress.xx + conf.stress.yy + conf.stress.zz) / 3,
            "lattice_a": np.linalg.norm(conf.lattice_vectors[0]),
            "lattice_b": np.linalg.norm(conf.lattice_vectors[1]),
            "lattice_c": np.linalg.norm(conf.lattice_vectors[2]),
        }

    return pd.DataFrame.from_records([conf_to_dict(conf) for conf in section.configurations])


def _render_images(section: MLABSection) -> dict[str, dict[str, QImage]]:
    min_energy_conf = min(section.configurations, key=attrgetter("energy"))
    max_energy_conf = max(section.configurations, key=attrgetter("energy"))

    image_size = (get_config()["rendering"]["width"], get_config()["rendering"]["height"])
    min_images = rendering.render(min_energy_conf, size=image_size)
    max_images = rendering.render(max_energy_conf, size=image_size)

    return {
        "min": min_images,
        "max": max_images,
    }


@dataclass
class Stats:
    general: pd.DataFrame
    rdfs: dict[str, tuple[ArrayLike, ArrayLike]]
    descriptors: dict[str, pd.DataFrame]

    images: dict[str, dict[str, QImage]]


def get_stats(section: MLABSection) -> Stats:
    return Stats(
        general=_calculate_general(section),
        rdfs=_calculate_rdfs(section),
        descriptors=_calculate_descriptors(section),
        images=_render_images(section),
    )
