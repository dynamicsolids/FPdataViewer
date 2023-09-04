import numpy as np
import pandas as pd
from dscribe.descriptors import SOAP, ACSF, LMBTR
from sklearn.decomposition import PCA

from mlab_tools.adapters.ase_adapter import section_to_atoms
from mlab_tools.structures import MLABSection
from mlab_viewer.config import get_config


def calculate_descriptors(section: MLABSection) -> dict[str, pd.DataFrame]:
    structures = get_config()["descriptors"]["structures"]

    if isinstance(structures, float) and 0. <= structures <= 1.:
        structures = int(structures * len(section.configurations))

    section_ase = section_to_atoms(section)
    section_ase = np.random.choice(section_ase, structures) if 1 <= structures < len(section_ase) else section_ase

    descriptor_object = get_descriptor_object(section)

    descriptors_per_type = {}

    for type, _ in section.number_of_atoms_per_type:
        print(f"\rcalculating descriptors for {type} ... ", end="")

        centers = [i for i, t in enumerate(section.generate_type_lookup()) if t == type]

        feature_vectors = descriptor_object.create(section_ase, centers=[centers for _ in section_ase], n_jobs=-1)
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


def get_descriptor_object(section: MLABSection):
    global_args = {
        "species": [type for type, _ in section.number_of_atoms_per_type],
        "periodic": True,
        "average": "off",
        "sparse": False,
        "dtype": "float32",
    }

    if "soap" in get_config()["descriptors"]:
        args = {}
        args.update(global_args)
        args.update(get_config()["descriptors"]["soap"])

        return SOAP(**args)

    elif "acsf" in get_config()["descriptors"]:
        args = {}
        args.update(global_args)
        args.update(get_config()["descriptors"]["acsf"])

        return ACSF(**args)

    elif "lmbtr" in get_config()["descriptors"]:
        args = {}
        args.update(global_args)
        args.update(get_config()["descriptors"]["lmbtr"])

        return LMBTR(**args)

    else:
        raise ValueError("no or unsupported descriptors named in config")
