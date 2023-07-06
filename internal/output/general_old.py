from abc import abstractmethod, ABC

import numpy as np
from output_matplotlib.figure import Figure
from output_matplotlib.gridspec import SubplotSpec

from internal.config import get_config
from internal.structures import MLABSection
from output_matplotlib import pyplot as plt


class Plot(ABC):
    def __init__(self, fig: Figure, section: MLABSection):
        self.fig = fig
        self.section = section

    @abstractmethod
    def create_axes(self, spec: SubplotSpec):
        raise NotImplementedError()


class EnergyPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        ax.hist([conf.energy for conf in self.section.configurations],
                bins=100, color="k")
        ax.set_xlabel("Energy [eV]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.grid(visible=True)


class StressPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        ax.hist([conf.stress.get_mechanical_pressure() for conf in self.section.configurations],
                bins=100, color="k")
        ax.set_xlabel("Mechanical pressure [kbar]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.grid(visible=True)


class ForcesPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        params = {"bins": 100,
                  "alpha": 0.7}

        ax.hist([abs(force) for conf in self.section.configurations for force in conf.forces[:, 0]],
                label="x", color="r",
                **params)
        ax.hist([abs(force) for conf in self.section.configurations for force in conf.forces[:, 1]],
                label="y", color="b",
                **params)
        ax.hist([abs(force) for conf in self.section.configurations for force in conf.forces[:, 2]],
                label="z", color="g",
                **params)
        ax.hist([np.linalg.norm(force) for conf in self.section.configurations for force in conf.forces],
                label="||.||", color="k",
                **params)

        ax.set_xlabel("Force [eV/ang]")
        ax.get_yaxis().set_ticks([])
        ax.legend()
        ax.minorticks_on()
        ax.grid(visible=True)


class LatticePlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        params = {"bins": 100,
                  "alpha": 0.8}

        ax.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in self.section.configurations],
                label="a", color="r",
                **params)
        ax.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in self.section.configurations],
                label="b", color="b",
                **params)
        ax.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in self.section.configurations],
                label="c", color="g",
                **params)
        ax.set_xlabel("Lattice vector length [ang]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.legend()
        ax.grid(visible=True)


class SplitLatticePlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        grid = spec.subgridspec(ncols=1, nrows=3, hspace=0)

        ax3 = self.fig.add_subplot(grid[2, 0])
        ax2 = self.fig.add_subplot(grid[1, 0], sharex=ax3)
        ax1 = self.fig.add_subplot(grid[0, 0], sharex=ax3)

        params = {"bins": 100,
                  "alpha": 0.8}

        ax1.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in self.section.configurations],
                 label="a", color="r",
                 **params)
        ax2.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in self.section.configurations],
                 label="b", color="b",
                 **params)
        ax3.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in self.section.configurations],
                 label="c", color="g",
                 **params)
        ax3.set_xlabel("Lattice vector length [ang]")
        ax1.get_yaxis().set_ticks([])
        ax2.get_yaxis().set_ticks([])
        ax3.get_yaxis().set_ticks([])
        ax3.minorticks_on()

        ax1.tick_params(labelbottom=False)
        ax2.tick_params(labelbottom=False)

        ax1.grid(visible=True)
        ax2.grid(visible=True)
        ax3.grid(visible=True)


def display(section: MLABSection):
    plots = [[EnergyPlot, ForcesPlot],
             [StressPlot, LatticePlot]]

    if get_config()["separate"]:
        for _, plot in np.ndenumerate(np.array(plots)):
            fig = plt.figure(num="General")
            grid = fig.add_gridspec(ncols=1, nrows=1)

            plot(fig, section).create_axes(grid[0, 0])
    else:
        fig = plt.figure(num="General", layout="tight")
        grid = fig.add_gridspec(ncols=2, nrows=2)

        for (i, j), plot in np.ndenumerate(np.array(plots)):
            plot(fig, section).create_axes(grid[i, j])


def display_general_info(section: MLABSection):
    atom_repr = ", ".join([f"{name} ({number})" for name, number in section.header.number_of_atoms_per_type])
    energies = [conf.energy for conf in section.configurations]
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    print()
    print(f"###### {section.header.name} ######")
    print(atom_repr)
    print(f"Structures: {len(section.configurations)}")
    print(f"Atoms: {section.header.number_of_atoms}")
    print()
    print(f"Energy: {mean_energy:.1f} eV \u00B1 {2 * std_energy:.2f} eV")
    print("#######" + len(section.header.name) * "#" + "#######")

    # TODO: Bounding box volume (average)
    # TODO: Bounding box min. non-overlapping sphere radius (average), useful for RDF
