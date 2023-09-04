import numpy as np
import pandas as pd

from mlab_tools.structures import MLABConfiguration, MLABSection


def calculate_misc(section: MLABSection) -> pd.DataFrame:
    def conf_to_dict(conf: MLABConfiguration) -> dict[str, float]:
        a = np.linalg.norm(conf.lattice_vectors[0])
        b = np.linalg.norm(conf.lattice_vectors[1])
        c = np.linalg.norm(conf.lattice_vectors[2])

        return {
            "energy": conf.energy,
            "pressure": -(conf.stress.xx + conf.stress.yy + conf.stress.zz) / 3,
            "lattice_a": a,
            "lattice_b": b,
            "lattice_c": c,
            "volume": a * b * c,
        }

    return pd.DataFrame.from_records([conf_to_dict(conf) for conf in section.configurations])
