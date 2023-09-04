from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from mlab_tools.structures import MLAB, MLABSection
from mlab_viewer import analysis
from mlab_viewer.plotting import *

_landscape_a4 = (11.69, 8.27)


def run(args, mlab: MLAB, sections: list[MLABSection]):
    metadata = {
        "Title": args.input_file.name,
        "Creator": "mlab_viewer",
    }

    with PdfPages(args.output_file, metadata=metadata, keep_empty=True) as pdf:
        plt.style.use("ggplot")

        plt.rcParams.update({
            "font.size": 6,
            "font.family": "monospace",
        })

        fig_params = {
            "figsize": _landscape_a4,
            "layout": "constrained",
            "rasterized": args.rasterize,
        }

        for i, section in enumerate(sections):
            section_metadata = analysis.gather_metadata(args, section)
            section_metadata.update({
                "file_name": args.input_file.name,
                "current_group": i + 1,
                "total_groups": len(sections),
            })

            print("\rcreating figures ... ", end="")

            fig = plt.figure(**fig_params)
            _make_overview_page(section, section_metadata, fig)
            pdf.savefig(dpi=600)
            plt.close()

            fig = plt.figure(**fig_params)
            _make_image_page(section, section_metadata, fig)
            pdf.savefig(dpi=600)
            plt.close()

            for type, _ in section.number_of_atoms_per_type:
                fig = plt.figure(**fig_params)
                _make_type_page(section, section_metadata, fig, type)
                pdf.savefig(dpi=600)
                plt.close()


def _make_overview_page(section: MLABSection, section_metadata: dict, fig: Figure):
    grid = fig.add_gridspec(ncols=3, nrows=3)

    fig.suptitle(f"[{section_metadata['current_group']}/{section_metadata['total_groups']}] {section_metadata['file_name']} ({section.name})", fontsize=12)

    fig_top_left = fig.add_subfigure(grid[0, 0:2], in_layout=True)
    fig_top_right = fig.add_subfigure(grid[0, 2], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1:, :], in_layout=True)

    # fig_top_left.set_facecolor("0.25")
    # fig_top_right.set_facecolor("0.50")
    # fig_bottom.set_facecolor("0.75")

    # fig_top_left.suptitle("ML_AB: New", fontsize=10)
    # fig_top_right.suptitle("front view", fontsize=10)
    # fig_bottom.suptitle("general", fontsize=10)

    grid_top_left = fig_top_left.add_gridspec(ncols=2, nrows=2)
    _plot_text_file    (section, section_metadata, fig_top_left.add_subplot(grid_top_left[0, 0]))
    _plot_text_group   (section, section_metadata, fig_top_left.add_subplot(grid_top_left[1, 0]))
    _plot_text_overview(section, section_metadata, fig_top_left.add_subplot(grid_top_left[:, 1]))

    grid_bottom = fig_bottom.add_gridspec(ncols=3, nrows=3)
    plot_energy_hist (section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[0, 0]))
    plot_energy_line (section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[0, 1:]))
    plot_lattice_hist(section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[1, 0]))
    plot_lattice_line(section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[1, 1:]))
    plot_stress_hist (section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[2, 0]))
    plot_stress_line (section_metadata["misc"], fig_bottom.add_subplot(grid_bottom[2, 1:]))

    grid_top_right = fig_top_right.add_gridspec(ncols=1, nrows=1)
    if "img" in section_metadata:
        plot_image(section_metadata["img"]["min"]["front"], "min energy configuration", fig_top_right.add_subplot(grid_top_right[0, 0]))


def _plot_text_group(section: MLABSection, section_metadata: dict, ax: Axes):
    atom_repr = ", ".join([f"{name} ({number})" for name, number in section.common_header.number_of_atoms_per_type])

    _plot_table("current structure group", [
        ["name", section.name, ""],
        ["structure group", f"{section_metadata['current_group']} (of {section_metadata['total_groups']} in file)", ""],
        ["structures", f"{len(section.configurations)} (of {len(section.source.configurations)} in file)", ""],
        ["atoms", atom_repr, ""],
        ["", f"{section.number_of_atoms} total", ""],
    ], ax)


def _plot_text_file(section: MLABSection, section_metadata: dict, ax: Axes):
    _plot_table("file", [
        ["name", section_metadata["file_name"], ""],
        ["structure groups", section_metadata["total_groups"], ""],
        ["total structures", len(section.source.configurations), ""],
    ], ax)


def _plot_text_overview(section: MLABSection, section_metadata: dict, ax: Axes):
    misc = section_metadata['misc']

    _plot_table("overview", [
        ["energy", f"{misc['energy'].mean():.1f} \u00B1 {misc['energy'].std():.2f}", "eV"],
        ["volume", f"{misc['volume'].mean():.1f} \u00B1 {misc['volume'].std():.2f}", "ang^3"],
        ["lattice vector a", f"{misc['lattice_a'].mean():.1f} \u00B1 {misc['lattice_a'].std():.2f}", "ang"],
        ["lattice vector b", f"{misc['lattice_b'].mean():.1f} \u00B1 {misc['lattice_b'].std():.2f}", "ang"],
        ["lattice vector c", f"{misc['lattice_c'].mean():.1f} \u00B1 {misc['lattice_c'].std():.2f}", "ang"],
        ["non-periodic distance", f"{section_metadata['non_periodic_distance']:.1f} (min. for group)", "ang"],
    ], ax)


def _plot_table(title: str, text: list[list[str]], ax: Axes):
    ax.set_title(title, loc="left")

    ax.set_axis_off()
    tab = ax.table(
        cellText=text,
        colWidths=[0.4, 0.5, 0.1],
        cellLoc="left",
        loc="upper left",
        edges="",
    )

    tab.auto_set_font_size(False)
    tab.set_fontsize(6)
    tab.scale(1, 1)


def _make_image_page(section: MLABSection, section_metadata: dict, fig: Figure):
    grid = fig.add_gridspec(ncols=3, nrows=2)

    fig_top = fig.add_subfigure(grid[0, :], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1, :], in_layout=True)

    # fig_top.set_facecolor("0.50")
    # fig_bottom.set_facecolor("0.75")

    # TODO: Are these configuration numbers correct when multiple sections exist?
    fig_top.suptitle(f"minimum energy configuration (structure {1 + min(range(len(section.configurations)), key=lambda i: section.configurations[i].energy)})", fontsize=10)
    fig_bottom.suptitle(f"maximum energy configuration (structure {1 + max(range(len(section.configurations)), key=lambda i: section.configurations[i].energy)})", fontsize=10)

    grid_top = fig_top.add_gridspec(ncols=3, nrows=1)
    if "img" in section_metadata:
        plot_image(section_metadata["img"]["min"]["perspective"], "perspective", fig_top.add_subplot(grid_top[0, 0]))
        plot_image(section_metadata["img"]["min"]["front"], "front", fig_top.add_subplot(grid_top[0, 1]))
        plot_image(section_metadata["img"]["min"]["top"], "top", fig_top.add_subplot(grid_top[0, 2]))

    grid_bottom = fig_bottom.add_gridspec(ncols=3, nrows=1)
    if "img" in section_metadata:
        plot_image(section_metadata["img"]["max"]["perspective"], "perspective", fig_bottom.add_subplot(grid_bottom[0, 0]))
        plot_image(section_metadata["img"]["max"]["front"], "front", fig_bottom.add_subplot(grid_bottom[0, 1]))
        plot_image(section_metadata["img"]["max"]["top"], "top", fig_bottom.add_subplot(grid_bottom[0, 2]))


def _make_type_page(section: MLABSection, section_metadata: dict, fig: Figure, type: str):
    grid = fig.add_gridspec(ncols=3, nrows=2)

    fig_top = fig.add_subfigure(grid[0, :], in_layout=True)
    fig_bottom = fig.add_subfigure(grid[1, :], in_layout=True)

    # fig_top.set_facecolor("0.50")
    # fig_bottom.set_facecolor("0.75")

    fig_top.suptitle(f"principal component analysis of descriptors ({type})", fontsize=10)
    fig_bottom.suptitle(f"radial distribution functions ({type})", fontsize=10)

    grid_top = fig_top.add_gridspec(ncols=3, nrows=1)
    if "desc" in section_metadata:
        plot_descriptors_density         (section_metadata["desc"][type], fig_top.add_subplot(grid_top[0, 0]))
        plot_descriptors_scatter_grouping(section_metadata["desc"][type], fig_top.add_subplot(grid_top[0, 1]))
        plot_descriptors_scatter_energy  (section_metadata["desc"][type], fig_top.add_subplot(grid_top[0, 2]))

    grid_bottom = fig_bottom.add_gridspec(ncols=1, nrows=1)
    if "rdf" in section_metadata:
        plot_rdf(section_metadata["rdf"], type, fig_bottom.add_subplot(grid_bottom[0, 0]))
