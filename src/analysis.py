import math

from src.structures import MLABConfiguration, MLABConfigurationHeader, Vector


def calculate_radial_histogram(header: MLABConfigurationHeader, configurations: list[MLABConfiguration], center: set[str], to: set[str], cutoff: float, bins: int) -> list[tuple[float, int]]:
    # TODO: Implement (parallelized) RDF calculation

    hist = [0] * bins
    hist_bins = list([i * cutoff / bins for i in range(bins)])
    type_lookup = header.generate_type_lookup()

    for conf in configurations:
        for center_index, center_pos in enumerate(conf.positions):
            if type_lookup[center_index] in center:
                for to_index, to_pos in enumerate(conf.positions):
                    if type_lookup[to_index] in to and to_index != center_index:
                        distance = Vector.get_distance(center_pos, to_pos)

                        if distance < cutoff:
                            hist[math.floor(distance / cutoff * bins)] += 1

    return list(zip(hist_bins, hist))
