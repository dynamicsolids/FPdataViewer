from internal.plotting import *
from internal.structures import MLABSection

def run(section: MLABSection, stats: Stats):
    # sns.set_theme(style="ticks")

    # A
    fig = plt.figure(num=f"MLAB: {section.name} A", layout="tight")
    grid = fig.add_gridspec(ncols=2, nrows=3)

    plot_energy_line (stats, fig.add_subplot(grid[0, 0]))
    plot_energy_hist (stats, fig.add_subplot(grid[0, 1]))
    plot_lattice_line(stats, fig.add_subplot(grid[1, 0]))
    plot_lattice_hist(stats, fig.add_subplot(grid[1, 1]))
    plot_stress_line (stats, fig.add_subplot(grid[2, 0]))
    plot_stress_hist (stats, fig.add_subplot(grid[2, 1]))

    # B
    fig = plt.figure(num=f"MLAB: {section.name} B", layout="tight")
    grid = fig.add_gridspec(ncols=3, nrows=2)

    plot_image(stats.images["min"]["perspective"], "perspective", fig.add_subplot(grid[0, 0]))
    plot_image(stats.images["min"]["front"],       "front",       fig.add_subplot(grid[0, 1]))
    plot_image(stats.images["min"]["top"],         "top",         fig.add_subplot(grid[0, 2]))

    plot_image(stats.images["max"]["perspective"], "perspective", fig.add_subplot(grid[1, 0]))
    plot_image(stats.images["max"]["front"],       "front",       fig.add_subplot(grid[1, 1]))
    plot_image(stats.images["max"]["top"],         "top",         fig.add_subplot(grid[1, 2]))

    # C
    fig = plt.figure(num=f"MLAB: {section.name} C", layout="tight")
    grid = fig.add_gridspec(ncols=1, nrows=1)

    plot_rdf(stats, fig.add_subplot(grid[0, 0]))

    # D
    fig = plt.figure(num=f"MLAB: {section.name} D", layout="tight")
    grid = fig.add_gridspec(ncols=3, nrows=len(stats.descriptors))

    for i, (name, descriptors) in enumerate(stats.descriptors.items()):
        plot_descriptors_scatter_grouping(descriptors, fig.add_subplot(grid[i, 0]))
        plot_descriptors_scatter_energy  (descriptors, fig.add_subplot(grid[i, 1]))
        plot_descriptors_density         (descriptors, fig.add_subplot(grid[i, 2]))

    # E
    fig = plt.figure(num=f"MLAB: {section.name} E", layout="tight")
    grid = fig.add_gridspec(ncols=4, nrows=section.number_of_atom_types)

    for i, (type, _) in enumerate(section.number_of_atoms_per_type):
        plot_force_hist   (section, type, fig.add_subplot(grid[i, 0]))
        plot_force_density(section, type, 0, fig.add_subplot(grid[i, 1]))
        plot_force_density(section, type, 1, fig.add_subplot(grid[i, 2]))
        plot_force_density(section, type, 2, fig.add_subplot(grid[i, 3]))

    plt.show()
