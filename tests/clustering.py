from dscribe.descriptors import SOAP
from matplotlib import pyplot as plt
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA

from mlab.adapters.ase_adapter import section_to_atoms
from mlab.parsing import load, split

with open("/mnt/c/Users/thijm/Documents/PycharmProjects/mlab/example_files/ML_AB_KAgSe") as file:
    mlab = load(file)

for section in split(mlab):
    print(f"Section: {section.name}")

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

    for type in [type for type, _ in section.number_of_atoms_per_type]:
        centers = [i for i, t in enumerate(section.generate_type_lookup()) if t == type]

        feature_vectors = soap.create(section_ase, centers=[centers for _ in section_ase], n_jobs=-1)
        feature_vectors = feature_vectors.reshape(-1, feature_vectors.shape[-1])
        print(len(feature_vectors))

        pca = PCA(n_components=2, copy=False)

        feature_vectors = pca.fit_transform(feature_vectors)
        print(len(feature_vectors))

        x_min = min(feature_vectors[:, 0])
        x_max = max(feature_vectors[:, 0])
        y_min = min(feature_vectors[:, 1])
        y_max = max(feature_vectors[:, 1])

        clustering = HDBSCAN(allow_single_cluster=True, n_jobs=-1, min_cluster_size=100)
        clustering.fit(feature_vectors)
        labels = clustering.labels_
        print(len(set(labels)) - (1 if -1 in labels else 0))

        plt.figure()
        plt.scatter(feature_vectors[:, 0], feature_vectors[:, 1], alpha=0.1)
        plt.xlim([x_min, x_max])
        plt.ylim([y_min, y_max])
        bar = plt.colorbar()

        plt.figure()
        plt.hexbin(feature_vectors[:, 0], feature_vectors[:, 1])
        plt.xlim([x_min, x_max])
        plt.ylim([y_min, y_max])
        plt.colorbar()

    plt.show()
