import itertools

import matplotlib.pyplot as plt

from internal.analysis import calculate_radial_distribution
from internal.config import get_config
from internal.structures import MLABSection


def _get_pairs_from_config(section: MLABSection, pairs_str: list[str]) -> list[tuple[str, str]]:
    atoms = [atom for atom, _ in section.common_header.number_of_atoms_per_type]

    pairs = set()

    for pair_str in pairs_str:
        atom1, atom2 = pair_str.split("-")

        if atom1 != "*" and atom1 not in atoms:
            continue
        if atom2 != "*" and atom2 not in atoms:
            continue

        for atom in atoms:
            atom1 = atom1 if atom1 != "*" else atom
            atom2 = atom2 if atom1 != "*" else atom

            pairs.add((atom1, atom2))

    return list(pairs)


def sectioner(iterable, n):
    it = iter(iterable)
    return iter(lambda: tuple(itertools.islice(it, n)), ())


def display_rdf(section: MLABSection, data_list, window_num: int | None):
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


def display(section: MLABSection):
    rmin = get_config()["rdf"]["r_min"]
    rmax = get_config()["rdf"]["r_max"]
    bin_number = get_config()["rdf"]["bin_number"]
    structure_number = get_config()["rdf"]["structures"]

    if structure_number < 1:
        structure_number = int(structure_number * len(section.configurations))

    pairs = _get_pairs_from_config(section, get_config()["rdf"]["pairs"])
    plots = []

    for center, to in pairs:
        print(f"Calculating radial distribution function {center}-{to}...")

        bins, data = calculate_radial_distribution(section, {center}, {to}, rmin, rmax, bin_number, structure_number)
        plots.append((center, to, bins, data))

    plots_per_window = list(sectioner(plots, 4))

    for i, plots_for_window in enumerate(plots_per_window):
        display_rdf(section, plots_for_window, i if len(plots_per_window) > 1 else None)
