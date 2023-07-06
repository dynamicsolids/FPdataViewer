from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PIL import Image
from PySide6.QtCore import QBuffer
from PySide6.QtGui import QImage
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec
from numpy.typing import ArrayLike

from internal import rendering
from internal.config import get_config
from internal.structures import MLABSection, MLABSectionStats

sns.set_theme(style="ticks")

_red = "tab:red"
_green = "tab:green"
_blue = "tab:blue"
_black = "black"
_white = "white"


def plot_energy_hist(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    ax.hist([conf.energy for conf in section.configurations],
            bins=get_config()["hist"]["bins"],
            color=_blue)
    ax.set_xlabel("energy [eV]")
    ax.set_ylabel("count")
    ax.get_yaxis().set_ticks([])
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_energy_line(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    ax.plot([conf.energy for conf in section.configurations],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("energy [eV]")
    ax.grid(visible=True)


def plot_stress_hist(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    ax.hist([conf.stress.get_mechanical_pressure() for conf in section.configurations],
            bins=get_config()["hist"]["bins"],
            color=_blue)
    ax.set_xlabel("mechanical pressure [kbar]")
    ax.set_ylabel("count")
    ax.get_yaxis().set_ticks([])
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_stress_line(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    ax.plot([conf.stress.get_mechanical_pressure() for conf in section.configurations],
            color=_blue)
    ax.set_xlabel("structure")
    ax.set_ylabel("mechanical pressure [kbar]")
    ax.grid(visible=True)


def plot_forces_hist(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    params = {
        "bins": get_config()["hist"]["bins"],
        "alpha": 0.7
    }

    ax.hist([abs(force) for conf in section.configurations for force in conf.forces[:, 0]],
            label="x",
            color=_red,
            **params)
    ax.hist([abs(force) for conf in section.configurations for force in conf.forces[:, 1]],
            label="y",
            color=_blue,
            **params)
    ax.hist([abs(force) for conf in section.configurations for force in conf.forces[:, 2]],
            label="z",
            color=_green,
            **params)
    # ax.hist([np.linalg.norm(force) for conf in section.configurations for force in conf.forces],
    #         label="||.||",
    #         color=_black,
    #         **params)
    ax.set_xlabel("force [eV/ang]")
    ax.set_ylabel("count")
    ax.set_xlim(left=0)
    ax.get_yaxis().set_ticks([])
    ax.legend()
    ax.minorticks_on()
    ax.grid(visible=True)
    ax.set_axisbelow(True)


def plot_lattice_hist(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    params = {
        "bins": get_config()["hist"]["bins"],
        "alpha": 0.7
    }

    ax.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in section.configurations],
            label="a",
            color=_red,
            **params)
    ax.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in section.configurations],
            label="b",
            color=_blue,
            **params)
    ax.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in section.configurations],
            label="c",
            color=_green,
            **params)
    ax.set_xlabel("lattice vector length [ang]")
    ax.set_ylabel("count")
    ax.get_yaxis().set_ticks([])
    ax.minorticks_on()
    ax.legend()
    ax.grid(visible=True)

def plot_lattice_line(section: MLABSection, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    ax.plot([np.linalg.norm(conf.lattice_vectors[0]) for conf in section.configurations],
            label="a",
            color=_red)
    ax.plot([np.linalg.norm(conf.lattice_vectors[1]) for conf in section.configurations],
            label="b",
            color=_blue)
    ax.plot([np.linalg.norm(conf.lattice_vectors[2]) for conf in section.configurations],
            label="c",
            color=_green)
    ax.set_xlabel("structure")
    ax.set_ylabel("lattice vector length [ang]")
    ax.legend()
    ax.grid(visible=True)


# def plot_lattice_hist(section: MLABSection, fig: Figure, spec: SubplotSpec):
#     grid = spec.subgridspec(ncols=1, nrows=3, hspace=0)
#
#     ax3 = fig.add_subplot(grid[2, 0])
#     ax2 = fig.add_subplot(grid[1, 0], sharex=ax3)
#     ax1 = fig.add_subplot(grid[0, 0], sharex=ax3)
#
#     params = {
#         "bins": get_config()["hist"]["bins"]
#     }
#
#     ax1.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in section.configurations],
#              label="a",
#              color=_red,
#              **params)
#     ax2.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in section.configurations],
#              label="b",
#              color=_blue,
#              **params)
#     ax3.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in section.configurations],
#              label="c",
#              color=_green,
#              **params)
#     ax3.set_xlabel("Lattice vector length [ang]")
#
#     ax1.get_yaxis().set_ticks([])
#     ax2.get_yaxis().set_ticks([])
#     ax3.get_yaxis().set_ticks([])
#     ax3.minorticks_on()
#
#     ax1.tick_params(labelbottom=False)
#     ax2.tick_params(labelbottom=False)
#
#     ax1.grid(visible=True)
#     ax2.grid(visible=True)
#     ax3.grid(visible=True)
#
#     ax1.set_axisbelow(True)
#     ax2.set_axisbelow(True)
#     ax3.set_axisbelow(True)


def plot_image(image: QImage, label: str, fig: Figure, spec: SubplotSpec):
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    image.save(buffer, "png")
    image = Image.open(BytesIO(buffer.data()))

    ax = fig.add_subplot(spec)

    ax.imshow(image)
    ax.set_xlabel(label)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    #ax.axis("off")


def plot_rdf(rdfs: dict[str, tuple[ArrayLike, ArrayLike]], fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    for name, (bins, data) in rdfs.items():
        ax.plot(bins, data, label=name)
    ax.set_xlabel("r [ang]")
    ax.set_ylabel("g(r)")
    ax.set_xlim(left=bins[0], right=bins[-1])
    ax.minorticks_on()
    ax.hlines(1, bins[0], bins[-1], linestyles="dashed", colors=_black)
    ax.grid(visible=True)
    ax.legend()


def plot_descriptors_scatter(descriptors: ArrayLike, type: str, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    x_min = min(descriptors[:, 0])
    x_max = max(descriptors[:, 0])
    y_min = min(descriptors[:, 1])
    y_max = max(descriptors[:, 1])

    # res = ax.scatter(descriptors[:, 0], descriptors[:, 1], alpha=0.1)
    # ax.set_xlabel("PC 1")
    # ax.set_ylabel("PC 2")
    # ax.set_xlim([x_min, x_max])
    # ax.set_ylim([y_min, y_max])
    # plt.colorbar(res, ax=ax)
    sns.scatterplot(x=descriptors[:, 0], y=descriptors[:, 1], s=5, color=_blue, ax=ax)
    sns.kdeplot(x=descriptors[:, 0], y=descriptors[:, 1], levels=7, color=(0., 0., 0., 0.5), ax=ax)
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])


def plot_descriptors_density(descriptors: ArrayLike, type: str, fig: Figure, spec: SubplotSpec):
    ax = fig.add_subplot(spec)

    x_min = min(descriptors[:, 0])
    x_max = max(descriptors[:, 0])
    y_min = min(descriptors[:, 1])
    y_max = max(descriptors[:, 1])

    res = ax.hexbin(descriptors[:, 0], descriptors[:, 1])
    ax.set_xlabel("PC 1")
    ax.set_ylabel("PC 2")
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])
    plt.colorbar(res, ax=ax)


def run(section: MLABSection, stats: MLABSectionStats):
    image_top, image_front = rendering.render(section, size=(1024, 1024))

    # A
    fig = plt.figure(num=f"MLAB: {section.name} A", layout="tight")
    grid = fig.add_gridspec(ncols=2, nrows=4)

    plot_energy_hist(section, fig, grid[0, 0])
    plot_energy_line(section, fig, grid[0, 1])
    plot_lattice_hist(section, fig, grid[1, 0])
    plot_lattice_line(section, fig, grid[1, 1])
    plot_stress_hist(section, fig, grid[2, 0])
    plot_stress_line(section, fig, grid[2, 1])
    plot_forces_hist(section, fig, grid[3, :])

    # B
    fig = plt.figure(num=f"MLAB: {section.name} B", layout="tight")
    grid = fig.add_gridspec(ncols=2, nrows=1)

    plot_image(image_top, "top (minimum energy)", fig, grid[0, 0])
    plot_image(image_front, "front (minimum energy)", fig, grid[0, 1])

    # C
    fig = plt.figure(num=f"MLAB: {section.name} C", layout="tight")
    grid = fig.add_gridspec(ncols=1, nrows=1)

    plot_rdf(stats.rdfs, fig, grid[0, 0])

    # D
    fig = plt.figure(num=f"MLAB: {section.name} D", layout="tight")
    grid = fig.add_gridspec(ncols=2, nrows=len(stats.descriptors))

    for i, (name, descriptors) in enumerate(stats.descriptors.items()):
        plot_descriptors_scatter(descriptors, name, fig, grid[i, 0])
        plot_descriptors_density(descriptors, name, fig, grid[i, 1])

    plt.show()
