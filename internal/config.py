# DEFAULT CONFIG - DO NOT EDIT - IGNORED WHEN mlab_config.json PRESENT
default_config = {
    "general": {
        "bins": 100
    },
    "rdf": {
        "bins": 1000,
        "structures": 0.1,
        "r_min": 1.0,
        "r_max": 10.0,
        "pairs": "same"
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
