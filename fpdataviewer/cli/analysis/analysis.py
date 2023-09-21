import numpy as np

from fpdataviewer.cli.config import get_config, set_config
from fpdataviewer.mlab.mlab import MLABSection

_original_config = None
_temporary_config = None

def gather_metadata(args, section: MLABSection) -> dict:
    global _original_config
    global _temporary_config

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

    if _original_config is None:
        _original_config = get_config()
    _temporary_config = _original_config.copy()
    find_and_replace(_temporary_config, "auto", 2. * min_offset)
    set_config(_temporary_config)

    from fpdataviewer.cli.analysis.misc import calculate_misc
    section_metadata["misc"] = calculate_misc(section)

    if "rdf" not in args.skip:
        from fpdataviewer.cli.analysis.rdfs import calculate_rdfs
        section_metadata["rdf"] = calculate_rdfs(section)

    if "desc" not in args.skip:
        from fpdataviewer.cli.analysis.descriptors import calculate_descriptors
        section_metadata["desc"] = calculate_descriptors(section)

    if "img" not in args.skip:
        from fpdataviewer.cli.analysis.images import render_images
        section_metadata["img"] = render_images(section)

    return section_metadata


def find_and_replace(config: dict, old_value: str, new_value: str):
    for key, value in config.items():
        if isinstance(value, dict):
            find_and_replace(value, old_value, new_value)
        elif value == old_value:
            config[key] = new_value
