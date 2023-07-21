from matplotlib.backends.backend_pdf import PdfPages

from internal.plotting import *
from internal.structures import MLABSection

_landscape_a4 = (11.69, 8.27)


def make_page_general(section: MLABSection, stats: Stats, pdf: PdfPages):
    fig = plt.figure(
        figsize=_landscape_a4,
        layout="constrained",
    )
    grid = fig.add_gridspec(ncols=3, nrows=3)

    fig_top_left = fig.add_subfigure(grid[0, 0], in_layout=True)
    fig_top_right = fig.add_subfigure(grid[0, 1:], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1:, :], in_layout=True)

    fig_top_left.set_facecolor("0.25")
    fig_top_right.set_facecolor("0.50")
    fig_bottom.set_facecolor("0.75")

    fig_top_left.suptitle("A", fontsize=12)
    fig_top_right.suptitle("B", fontsize=12)
    fig_bottom.suptitle("C", fontsize=12)

    grid_bottom = fig_bottom.add_gridspec(ncols=3, nrows=3)
    plot_energy_hist (stats, fig_bottom.add_subplot(grid_bottom[0, 0]))
    plot_energy_line (stats, fig_bottom.add_subplot(grid_bottom[0, 1:]))
    plot_lattice_hist(stats, fig_bottom.add_subplot(grid_bottom[1, 0]))
    plot_lattice_line(stats, fig_bottom.add_subplot(grid_bottom[1, 1:]))
    plot_stress_hist (stats, fig_bottom.add_subplot(grid_bottom[2, 0]))
    plot_stress_line (stats, fig_bottom.add_subplot(grid_bottom[2, 1:]))

    grid_top_right = fig_top_right.add_gridspec(ncols=2, nrows=1)
    plot_image(stats.images["min"]["front"], "Min energy configuration", fig_top_right.add_subplot(grid_top_right[0, 0]))
    plot_image(stats.images["max"]["front"], "Max energy configuration", fig_top_right.add_subplot(grid_top_right[0, 1]))

    pdf.savefig(dpi=600)
    plt.close()


def make_page_images(section: MLABSection, stats: Stats, pdf: PdfPages):
    fig = plt.figure(
        figsize=_landscape_a4,
        layout="constrained",
    )
    grid = fig.add_gridspec(ncols=3, nrows=2)

    fig_top = fig.add_subfigure(grid[0, :], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1, :], in_layout=True)

    fig_top.set_facecolor("0.50")
    fig_bottom.set_facecolor("0.75")

    fig_top.suptitle(f"min ({min(range(len(section.configurations)), key=lambda i: section.configurations[i].energy)})", fontsize=12)
    fig_bottom.suptitle(f"max ({max(range(len(section.configurations)), key=lambda i: section.configurations[i].energy)})", fontsize=12)

    grid_top = fig_top.add_gridspec(ncols=3, nrows=1)
    plot_image(stats.images["min"]["perspective"], "perspective", fig_top.add_subplot(grid_top[0, 0]))
    plot_image(stats.images["min"]["front"], "front", fig_top.add_subplot(grid_top[0, 1]))
    plot_image(stats.images["min"]["top"], "top", fig_top.add_subplot(grid_top[0, 2]))

    grid_bottom = fig_bottom.add_gridspec(ncols=3, nrows=1)
    plot_image(stats.images["max"]["perspective"], "perspective", fig_bottom.add_subplot(grid_bottom[0, 0]))
    plot_image(stats.images["max"]["front"], "front", fig_bottom.add_subplot(grid_bottom[0, 1]))
    plot_image(stats.images["max"]["top"], "top", fig_bottom.add_subplot(grid_bottom[0, 2]))

    pdf.savefig(dpi=600)
    plt.close()


def make_page_rdf(section: MLABSection, stats: Stats, pdf: PdfPages):
    fig = plt.figure(
        figsize=_landscape_a4,
        layout="constrained",
    )
    grid = fig.add_gridspec(ncols=4, nrows=5)

    plot_rdf(stats, fig.add_subplot(grid[0, 1:]))
    plot_rdf(stats, fig.add_subplot(grid[1, 1:]))
    plot_rdf(stats, fig.add_subplot(grid[2, 1:]))
    plot_rdf(stats, fig.add_subplot(grid[3, 1:]))
    plot_rdf(stats, fig.add_subplot(grid[4, 1:]))

    pdf.savefig()
    plt.close()


def make_page_type(section: MLABSection, stats: Stats, pdf: PdfPages, type: str):
    fig = plt.figure(
        figsize=_landscape_a4,
        layout="constrained",
    )
    grid = fig.add_gridspec(ncols=3, nrows=2)

    fig_top = fig.add_subfigure(grid[0, :], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1, :], in_layout=True)

    fig_top.set_facecolor("0.50")
    fig_bottom.set_facecolor("0.75")

    fig_top.suptitle(f"A ({type})", fontsize=12)
    fig_bottom.suptitle(f"B ({type})", fontsize=12)

    grid_bottom = fig_bottom.add_gridspec(ncols=3, nrows=1)
    plot_descriptors_density         (stats.descriptors[type], fig_bottom.add_subplot(grid_bottom[0, 0]))
    plot_descriptors_scatter_grouping(stats.descriptors[type], fig_bottom.add_subplot(grid_bottom[0, 1]))
    plot_descriptors_scatter_energy  (stats.descriptors[type], fig_bottom.add_subplot(grid_bottom[0, 2]))

    grid_top = fig_top.add_gridspec(ncols=3, nrows=1)
    # plot_force_hist   (section, type,    fig.add_subplot(grid[1, 0]))
    plot_force_density(section, type, 0, fig_top.add_subplot(grid_top[0, 0]))
    plot_force_density(section, type, 1, fig_top.add_subplot(grid_top[0, 1]))
    plot_force_density(section, type, 2, fig_top.add_subplot(grid_top[0, 2]))

    pdf.savefig()
    plt.close()

def run(section: MLABSection, stats: Stats):
    metadata = {
        "Title": section.name,
        "Subject": f"Data visualization",
        "Creator": "mlab",
    }

    with PdfPages("output.pdf", metadata=metadata, keep_empty=False) as pdf:
        plt.style.use("ggplot")

        plt.rcParams.update({
            "font.size": 6,
        })

        make_page_general(section, stats, pdf)
        make_page_images(section, stats, pdf)
        for type, _ in section.number_of_atoms_per_type:
            make_page_type(section, stats, pdf, type)
        make_page_rdf(section, stats, pdf)
