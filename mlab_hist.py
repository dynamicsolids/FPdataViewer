import argparse
from abc import ABC, abstractmethod

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import SubplotSpec

from mlab.initialization import init, print_stats
from mlab.structures import MLABGroup


class Plot(ABC):
    def __init__(self, fig: Figure, group: MLABGroup, config: dict):
        self.fig = fig
        self.group = group
        self.config = config

    @abstractmethod
    def create_axes(self, spec: SubplotSpec):
        raise NotImplementedError()


class EnergyPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        ax.hist([conf.energy for conf in self.group.configurations],
                bins=100, color="k")
        ax.set_xlabel("Energy [eV]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.grid(True)


class StressPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        ax.hist([conf.stress.get_mechanical_pressure() for conf in self.group.configurations],
                bins=100, color="k")
        ax.set_xlabel("Mechanical pressure [kbar]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.grid(True)


class ForcesPlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        params = {"bins": 100,
                  "alpha": 0.7}

        ax.hist([abs(force) for conf in self.group.configurations for force in conf.forces[:, 0]],
                label="x", color="r",
                **params)
        ax.hist([abs(force) for conf in self.group.configurations for force in conf.forces[:, 1]],
                label="y", color="b",
                **params)
        ax.hist([abs(force) for conf in self.group.configurations for force in conf.forces[:, 2]],
                label="z", color="g",
                **params)
        ax.hist([np.linalg.norm(force) for conf in self.group.configurations for force in conf.forces],
                label="||.||", color="k",
                **params)

        ax.set_xlabel("Force [eV/ang]")
        ax.get_yaxis().set_ticks([])
        ax.legend()
        ax.minorticks_on()
        ax.grid(True)


class LatticePlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        ax = self.fig.add_subplot(spec)

        params = {"bins": 100,
                  "alpha": 0.8}

        ax.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in self.group.configurations],
                label="a", color="r",
                **params)
        ax.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in self.group.configurations],
                label="b", color="b",
                **params)
        ax.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in self.group.configurations],
                label="c", color="g",
                **params)
        ax.set_xlabel("Lattice vector length [ang]")
        ax.get_yaxis().set_ticks([])
        ax.minorticks_on()
        ax.legend()
        ax.grid(True)


class SplitLatticePlot(Plot):
    def create_axes(self, spec: SubplotSpec):
        grid = spec.subgridspec(ncols=1, nrows=3, hspace=0)

        ax3 = self.fig.add_subplot(grid[2, 0])
        ax2 = self.fig.add_subplot(grid[1, 0], sharex=ax3)
        ax1 = self.fig.add_subplot(grid[0, 0], sharex=ax3)

        params = {"bins": 100,
                  "alpha": 0.8}

        ax1.hist([np.linalg.norm(conf.lattice_vectors[0]) for conf in self.group.configurations],
                 label="a", color="r",
                 **params)
        ax2.hist([np.linalg.norm(conf.lattice_vectors[1]) for conf in self.group.configurations],
                 label="b", color="b",
                 **params)
        ax3.hist([np.linalg.norm(conf.lattice_vectors[2]) for conf in self.group.configurations],
                 label="c", color="g",
                 **params)
        ax3.set_xlabel("Lattice vector length [ang]")
        ax1.get_yaxis().set_ticks([])
        ax2.get_yaxis().set_ticks([])
        ax3.get_yaxis().set_ticks([])
        ax3.minorticks_on()

        ax1.tick_params(labelbottom=False)
        ax2.tick_params(labelbottom=False)

        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)


def view(group: MLABGroup, config: dict):
    plots = [[EnergyPlot, ForcesPlot],
             [StressPlot, SplitLatticePlot]]

    if config["hist"]["separate"]:
        for _, plot in np.ndenumerate(np.array(plots)):
            fig = plt.figure()
            grid = fig.add_gridspec(ncols=1, nrows=1)

            plot(fig, group, config).create_axes(grid[0, 0])
    else:
        fig = plt.figure(layout="tight")
        grid = fig.add_gridspec(ncols=2, nrows=2)

        for (i, j), plot in np.ndenumerate(np.array(plots)):
            plot(fig, group, config).create_axes(grid[i, j])

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="reads ML_AB files and displays various statistics")

    gs, c = init(parser)

    for g in gs:
        print_stats(g, c)
        view(g, c)
