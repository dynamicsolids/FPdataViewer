# DEFAULT CONFIG - DO NOT EDIT - IGNORED WHEN mlab_config.json PRESENT
default_config = {
    "general": {
        "bin_number": 100
    },
    "rdf": {
        "bin_number": 1000,
        "structures": 0.1,
        "r_min": 0.0,
        "r_max": 10.0,
        "pairs": ["any-any"]
    }
}

_config: dict | None = None


def get_config() -> dict:
    global _config

    if _config is None:
        raise ValueError("Config not loaded")

    return _config


def set_config(config: dict):
    global _config

    if _config is not None:
        raise ValueError("Config already loaded")

    _config = config
