import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image
from matplotlib import pyplot as plt, cm
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap

from src.internal.config import get_config

_red = "tab:red"
_green = "tab:green"
_blue = "tab:blue"
_black = "black"
_white = "white"


def plot_energy_hist(misc: pd.DataFrame, ax: Axes):
    ax.hist(misc["energy"],
            bins=get_config()["global"]["bins"],
            color=_blue)
    ax.set_xlabel("energy [eV]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_energy_line(misc: pd.DataFrame, ax: Axes):
    ax.plot(misc["energy"],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("energy [eV]")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_stress_hist(misc: pd.DataFrame, ax: Axes):
    ax.hist(misc["pressure"],
            bins=get_config()["global"]["bins"],
            color=_blue)
    ax.set_xlabel("mechanical pressure [kbar]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_stress_line(misc: pd.DataFrame, ax: Axes):
    ax.plot(misc["pressure"],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("mechanical pressure [kbar]")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_lattice_hist(misc: pd.DataFrame, ax: Axes):
    bins = np.histogram_bin_edges(np.hstack((misc["lattice_a"], misc["lattice_b"], misc["lattice_c"])),
                                  bins=get_config()["global"]["bins"])

    ax.hist(misc["lattice_a"], bins, label="a", color=_red)
    ax.hist(misc["lattice_b"], bins, label="b", color=_blue)
    ax.hist(misc["lattice_c"], bins, label="c", color=_green)
    ax.set_xlabel("lattice vector length [ang]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_lattice_line(misc: pd.DataFrame, ax: Axes):
    ax.plot(misc["lattice_a"], label="a", color=_red)
    ax.plot(misc["lattice_b"], label="b", color=_blue)
    ax.plot(misc["lattice_c"], label="c", color=_green)
    ax.set_xlabel("structure")
    ax.set_ylabel("lattice vector length [ang]")
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_image(image: Image, label: str, ax: Axes):
    if image is not None:
        ax.imshow(image)

    ax.set_ylabel(label)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    # ax.axis("off")
    ax.spines[["right", "top", "left", "bottom"]].set_visible(False)


def plot_rdf(rdf: dict | None, center_type: str | None, ax: Axes):
    for (atom1, atom2), (counts, bins) in rdf.items():
        # sns.histplot(weights=counts, bins=bins, label=name)
        if center_type == atom1:
            ax.stairs(counts, bins, label=f"{atom1}-{atom2}")
        elif center_type == atom2:
            ax.stairs(counts, bins, label=f"{atom2}-{atom1}")
        elif center_type is None and atom1 == atom2:
            ax.stairs(counts, bins, label=f"{atom1}-{atom2}")

    ax.set_xlabel("r [ang]")
    ax.set_ylabel("g(r)")
    ax.set_xlim(left=get_config()["rdf"]["r_min"], right=get_config()["rdf"]["r_max"])
    ax.minorticks_on()
    ax.axhline(y=1, color=_black, linestyle="dashed")
    ax.grid(visible=True)
    ax.set_axisbelow(True)
    ax.legend()


def plot_descriptors_scatter_grouping(desc: pd.DataFrame, ax: Axes):
    x_min = desc["pc_1"].min()
    x_max = desc["pc_1"].max()
    y_min = desc["pc_2"].min()
    y_max = desc["pc_2"].max()

    ndata = desc
    bdata = desc[desc["basis"] == True]
    ax.scatter(x=ndata["pc_1"], y=ndata["pc_2"], s=1, c=_blue, marker=".", label="Atom")
    ax.scatter(x=bdata["pc_1"], y=bdata["pc_2"], s=1, c=_red, marker="o", label="Atom in basis set")
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    ax.legend()


def plot_descriptors_density(desc: pd.DataFrame, ax: Axes):
    x_min = desc["pc_1"].min()
    x_max = desc["pc_1"].max()
    y_min = desc["pc_2"].min()
    y_max = desc["pc_2"].max()

    # _, _, _, res = ax.hist2d(x=data["pc_1"], y=data["pc_2"], bins=100)
    # res = ax.hexbin(data=data, x="pc_1", y="pc_2")
    sns.scatterplot(data=desc, x="pc_1", y="pc_2", s=3, color=".15", ax=ax)
    # sns.histplot(data=data, x="pc_1", y="pc_2", pthresh=.1, cmap="mako", cbar=True, cbar_kws={"label": "count"}, ax=ax)
    sns.histplot(data=desc, x="pc_1", y="pc_2", pthresh=.1, cmap="mako", ax=ax)
    sns.kdeplot(data=desc, x="pc_1", y="pc_2", levels=7, color=_white, linewidths=1, ax=ax)
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    # plt.colorbar(res, label="count", ax=ax)


def plot_descriptors_scatter_energy(desc: pd.DataFrame, ax: Axes):
    x_min = desc["pc_1"].min()
    x_max = desc["pc_1"].max()
    y_min = desc["pc_2"].min()
    y_max = desc["pc_2"].max()

    cmap_resolution = 512
    cmap = cm.get_cmap("coolwarm", cmap_resolution)
    energy_min = desc["energy"].min()
    energy_max = desc["energy"].max()

    # sort and map all energies to [0, 1]
    sorted_scaled_energies = (np.sort(desc["energy"]) - energy_min) / (energy_max - energy_min)

    # finds index of nearest mapped energy
    def find_nearest(value):
        return (np.abs(sorted_scaled_energies - value)).argmin() / len(sorted_scaled_energies)

    # remap color map to obtain good color distribution
    cmap = LinearSegmentedColormap.from_list("remapped", list(map(cmap, map(find_nearest, np.linspace(0, 1, cmap_resolution)))))

    # sns.scatterplot(data=data, x="PC 1", y="PC 2", s=5, color=_blue, hue="energy", ax=ax)
    res = ax.scatter(x=desc["pc_1"], y=desc["pc_2"], s=3, c=desc["energy"], marker=".", cmap=cmap)
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    plt.colorbar(res, label="energy [eV]", ax=ax)


# def plot_force_hist(section: MLABSection, type: str, ax: Axes):
#     type_indices = [i for (i, t) in enumerate(section.generate_type_lookup()) if t == type]
#
#     forces = np.array([abs(force) for conf in section.configurations for force in conf.forces[type_indices, :]])
#
#     bins = np.histogram_bin_edges(np.hstack((forces[:, 0], forces[:, 1], forces[:, 2])),
#                                   bins=get_config()["global"]["bins"])
#
#     ax.hist(forces[:, 0], bins, label="x", color=_red, alpha=0.6)
#     ax.hist(forces[:, 1], bins, label="y", color=_blue, alpha=0.4)
#     ax.hist(forces[:, 2], bins, label="z", color=_green, alpha=0.2)
#     ax.set_xlabel("force [eV/ang]")
#     ax.set_ylabel("count")
#     ax.set_xlim(left=0)
#     ax.minorticks_on()
#     ax.legend()
#     ax.grid(visible=True)
#     ax.set_axisbelow(True)
#
#
# def plot_force_density(section: MLABSection, type: str, component: int, ax: Axes):
#     y_max = max([abs(force) for conf in section.configurations for force in conf.forces.flatten()])
#
#     type_indices = [i for (i, t) in enumerate(section.generate_type_lookup()) if t == type]
#
#     forces = np.array([(i, force) for (i, conf) in enumerate(section.configurations) for force in conf.forces[type_indices, component]])
#
#     ax.axhline(y=0, color=_black, linestyle="dashed")
#     sns.histplot(x=forces[:, 0], y=forces[:, 1], discrete=(True, False), ax=ax)
#     ax.set_xlabel("structure")
#     ax.set_ylabel("force [eV/ang]")
#     ax.set_xlim(left=0, right=len(section.configurations))
#     ax.set_ylim(bottom=-y_max, top=y_max)
#     ax.grid(axis="y", visible=True)
#     ax.set_axisbelow(True)
