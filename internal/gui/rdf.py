import itertools

from matplotlib import pyplot as plt

from internal.analysis import calculate_radial_distribution
from internal.config import get_config
from internal.structures import MLABGroup


def _get_pairs(group: MLABGroup, pairs: list[str]) -> list[tuple[str, str]]:
    atoms = [atom for atom, _ in group.header.number_of_atoms_per_type]

    for pair in pairs:
        atom1, atom2 = pair.split("-")

        if atom1 not in atoms and atom1 != "any":
            continue
        if atom2 not in atoms and atom2 != "any":
            continue

        for atom in atoms:
            yield atom1 if atom1 != "any" else atom, atom2 if atom2 != "any" else atom


def grouper(iterable, n):
    it = iter(iterable)
    return iter(lambda: tuple(itertools.islice(it, n)), ())


def display_rdf(group: MLABGroup, data_list, window_num: int | None):
    plot_num = len(data_list)

    fig = plt.figure(num=f"Radial Distribution Functions ({window_num})" if window_num is not None else "Radial Distribution Functions",
                     layout="tight")
    grid = fig.add_gridspec(ncols=4, nrows=plot_num)

    for i, (center, to, bins, data) in enumerate(data_list):
        ax = fig.add_subplot(grid[i, :])
        ax.plot(bins, data, label=f"{center}-{to}")
        ax.set_xlabel("r [ang]")
        ax.set_ylabel("g(r)")
        ax.minorticks_on()
        ax.hlines(1, bins[0], bins[-1], linestyles="dashed")
        ax.grid(visible=True)
        ax.legend()


def display(group: MLABGroup):
    rmin = get_config()["rdf"]["r_min"]
    rmax = get_config()["rdf"]["r_max"]
    bin_number = get_config()["rdf"]["bin_number"]
    structure_number = get_config()["rdf"]["structures"]

    if structure_number < 1:
        structure_number = int(structure_number * len(group.configurations))

    pairs = set(_get_pairs(group, get_config()["rdf"]["pairs"]))
    plots = []

    for center, to in pairs:
        print(f"Calculating radial distribution function {center}-{to}...")

        bins, data = calculate_radial_distribution(group, {center}, {to}, rmin, rmax, bin_number, structure_number)
        plots.append((center, to, bins, data))

    plots_per_window = list(grouper(plots, 4))

    for i, plots_for_window in enumerate(plots_per_window):
        display_rdf(group, plots_for_window, i if len(plots_per_window) > 1 else None)
