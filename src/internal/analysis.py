import numpy as np

from mlab.mlab import MLABSection
from src.internal.config import get_config


def gather_metadata(args, section: MLABSection) -> dict:
    section_metadata = {}

    min_offset = float("inf")
    offset_matrix = np.array([[x, y, z]
                              for x in [-1, 0, 1]
                              for y in [-1, 0, 1]
                              for z in [-1, 0, 1]
                              if not x == y == z == 0])
    for conf in section.configurations:
        offset = min(np.linalg.norm(offset_matrix @ conf.lattice_vectors, axis=1))
        if offset < min_offset:
            min_offset = offset

    min_offset /= 2

    section_metadata["non_periodic_radius"] = min_offset
    find_and_replace(get_config(), "auto", 1.5 * min_offset)

    from src.internal.processing.misc import calculate_misc
    section_metadata["misc"] = calculate_misc(section)

    if "rdf" not in args.skip:
        from  src.internal.processing.rdfs import calculate_rdfs
        section_metadata["rdf"] = calculate_rdfs(section)

    if "desc" not in args.skip:
        from  src.internal.processing.descriptors import calculate_descriptors
        section_metadata["desc"] = calculate_descriptors(section)

    if "img" not in args.skip:
        from  src.internal.processing.images import render_images
        section_metadata["img"] = render_images(section)

    return section_metadata


# TODO: Does this work with multiple sections? Maybe integrate with "structures" fields
def find_and_replace(config: dict, old_value: str, new_value: str):
    for key, value in config.items():
        if isinstance(value, dict):
            find_and_replace(value, old_value, new_value)
        elif value == old_value:
            config[key] = new_value
