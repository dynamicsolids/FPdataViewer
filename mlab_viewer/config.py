default_config = {
    "global": {
        "bins": 100
    },
    "rdf": {
        "bins": 1000,
        "structures": 1.0,
        "r_min": 0.0,
        "r_max": "auto",
        "skip_pairs": []
    },
    "rendering": {
        "width": 1024,
        "height": 1024
    },
    "descriptors": {
        "structures": 1.0,
        "soap": {
            "r_cut": "auto",
            "n_max": 8,
            "l_max": 8
        }
    }
}

_config: dict | None = None


# TODO: implement everywhere
def get_config_item(*path: str):
    config = get_config()

    for item in path:
        if item in config:
            config = config[item]
        else:
            full_path = ".".join(path)
            raise ConfigError(f"could not find expected parameter \"{full_path}\" in config")

    return config


def get_config() -> dict:
    global _config

    if _config is None:
        raise ConfigError("config not loaded")

    return _config


def set_config(config: dict):
    global _config

    if _config is not None:
        raise ConfigError("config has already been loaded")

    _config = config


class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)
