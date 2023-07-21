from io import BytesIO

import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image
from PySide6.QtCore import QBuffer
from PySide6.QtGui import QImage
from matplotlib import pyplot as plt, cm
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap

from internal.analysis import Stats
from internal.config import get_config
from internal.structures import MLABSection

_red = "tab:red"
_green = "tab:green"
_blue = "tab:blue"
_black = "black"
_white = "white"


def plot_energy_hist(stats: Stats, ax: Axes):
    ax.hist(stats.general["energy"],
            bins=get_config()["global"]["bins"],
            color=_blue)
    ax.set_xlabel("energy [eV]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_energy_line(stats: Stats, ax: Axes):
    ax.plot(stats.general["energy"],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("energy [eV]")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_stress_hist(stats: Stats, ax: Axes):
    ax.hist(stats.general["pressure"],
            bins=get_config()["global"]["bins"],
            color=_blue)
    ax.set_xlabel("mechanical pressure [kbar]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_stress_line(stats: Stats, ax: Axes):
    ax.plot(stats.general["pressure"],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("mechanical pressure [kbar]")
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_lattice_hist(stats: Stats, ax: Axes):
    bins = np.histogram_bin_edges(np.hstack((stats.general["lattice_a"], stats.general["lattice_b"], stats.general["lattice_c"])),
                                  bins=get_config()["global"]["bins"])

    ax.hist(stats.general["lattice_a"], bins, label="a", color=_red)
    ax.hist(stats.general["lattice_b"], bins, label="b", color=_blue)
    ax.hist(stats.general["lattice_c"], bins, label="c", color=_green)
    ax.set_xlabel("lattice vector length [ang]")
    ax.set_ylabel("count")
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_lattice_line(stats: Stats, ax: Axes):
    ax.plot(stats.general["lattice_a"], label="a", color=_red)
    ax.plot(stats.general["lattice_b"], label="b", color=_blue)
    ax.plot(stats.general["lattice_c"], label="c", color=_green)
    ax.set_xlabel("structure")
    ax.set_ylabel("lattice vector length [ang]")
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_image(image: QImage, label: str, ax: Axes):
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    image.save(buffer, "png")
    image = Image.open(BytesIO(buffer.data()))

    ax.imshow(image)
    ax.set_ylabel(label)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    # ax.axis("off")
    ax.spines[["right", "top"]].set_visible(False)


def plot_rdf(stats: Stats, ax: Axes):
    for name, (counts, bins) in stats.rdfs.items():
        # sns.histplot(weights=counts, bins=bins, label=name)
        ax.stairs(counts, bins, label=name)
    ax.set_xlabel("r [ang]")
    ax.set_ylabel("g(r)")
    ax.set_xlim(left=bins[0], right=bins[-1])
    ax.minorticks_on()
    ax.axhline(y=1, color=_black, linestyle="dashed")
    ax.grid(visible=True)
    ax.set_axisbelow(True)
    ax.legend()


def plot_descriptors_scatter_grouping(data: pd.DataFrame, ax: Axes):
    x_min = data["pc_1"].min()
    x_max = data["pc_1"].max()
    y_min = data["pc_2"].min()
    y_max = data["pc_2"].max()

    ndata = data
    bdata = data[data["basis"] == True]
    ax.scatter(x=ndata["pc_1"], y=ndata["pc_2"], s=1, c=_blue, marker=".", label="Atom")
    ax.scatter(x=bdata["pc_1"], y=bdata["pc_2"], s=1, c=_red, marker="o", label="Atom in basis set")
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    ax.legend()


def plot_descriptors_density(data: pd.DataFrame, ax: Axes):
    x_min = data["pc_1"].min()
    x_max = data["pc_1"].max()
    y_min = data["pc_2"].min()
    y_max = data["pc_2"].max()

    # _, _, _, res = ax.hist2d(x=data["pc_1"], y=data["pc_2"], bins=100)
    # res = ax.hexbin(data=data, x="pc_1", y="pc_2")
    sns.scatterplot(data=data, x="pc_1", y="pc_2", s=3, color=".15", ax=ax)
    # sns.histplot(data=data, x="pc_1", y="pc_2", pthresh=.1, cmap="mako", cbar=True, cbar_kws={"label": "count"}, ax=ax)
    sns.histplot(data=data, x="pc_1", y="pc_2", pthresh=.1, cmap="mako", ax=ax)
    sns.kdeplot(data=data, x="pc_1", y="pc_2", levels=7, color=_white, linewidths=1, ax=ax)
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    # plt.colorbar(res, label="count", ax=ax)


def plot_descriptors_scatter_energy(data: pd.DataFrame, ax: Axes):
    x_min = data["pc_1"].min()
    x_max = data["pc_1"].max()
    y_min = data["pc_2"].min()
    y_max = data["pc_2"].max()

    res = 512
    emin = data["energy"].min()
    emax = data["energy"].max()
    a = (np.sort(data["energy"]) - emin) / (emax - emin)
    def find_nearest(value):
        return (np.abs(a - value)).argmin() / len(a)
    cmap = cm.get_cmap("coolwarm", res)
    cmap = LinearSegmentedColormap.from_list("remapped", list(map(cmap, map(find_nearest, np.linspace(0, 1, res)))))

    # sns.scatterplot(data=data, x="PC 1", y="PC 2", s=5, color=_blue, hue="energy", ax=ax)
    res = ax.scatter(x=data["pc_1"], y=data["pc_2"], s=3, c=data["energy"], marker=".", cmap=cmap)
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    plt.colorbar(res, label="energy [eV]", ax=ax)


def plot_force_hist(section: MLABSection, type: str, ax: Axes):
    type_indices = [i for (i, t) in enumerate(section.generate_type_lookup()) if t == type]

    forces = np.array([abs(force) for conf in section.configurations for force in conf.forces[type_indices, :]])

    bins = np.histogram_bin_edges(np.hstack((forces[:, 0], forces[:, 1], forces[:, 2])),
                                  bins=get_config()["global"]["bins"])

    ax.hist(forces[:, 0], bins, label="x", color=_red, alpha=0.6)
    ax.hist(forces[:, 1], bins, label="y", color=_blue, alpha=0.4)
    ax.hist(forces[:, 2], bins, label="z", color=_green, alpha=0.2)
    ax.set_xlabel("force [eV/ang]")
    ax.set_ylabel("count")
    ax.set_xlim(left=0)
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_force_density(section: MLABSection, type: str, component: int, ax: Axes):
    y_max = max([abs(force) for conf in section.configurations for force in conf.forces.flatten()])

    type_indices = [i for (i, t) in enumerate(section.generate_type_lookup()) if t == type]

    forces = np.array([(i, force) for (i, conf) in enumerate(section.configurations) for force in conf.forces[type_indices, component]])

    ax.axhline(y=0, color=_black, linestyle="dashed")
    sns.histplot(x=forces[:, 0], y=forces[:, 1], discrete=(True, False), ax=ax)
    ax.set_xlabel("structure")
    ax.set_ylabel("force [eV/ang]")
    ax.set_xlim(left=0, right=len(section.configurations))
    ax.set_ylim(bottom=-y_max, top=y_max)
    ax.grid(axis="y", visible=True)
    ax.set_axisbelow(True)