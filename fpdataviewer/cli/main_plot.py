from __future__ import annotations

import json

from fpdataviewer.cli.config import set_config, default_config
from fpdataviewer.mlab import parsing, validation


def plot(args) -> None:
    # Load config
    config = default_config

    if args.config_file is not None:
        with args.config_file.open(mode="rt") as file:
            config.update(json.load(file))

    set_config(config)

    # Load MLAB file
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)
    if args.strict:
        validation.validate(mlab)

    # Plot
    if args.interactive:
        import fpdataviewer.cli.plotting.plot_mpl as output
    else:
        import fpdataviewer.cli.plotting.plot_pdf as output

    output.run(args, mlab)

    print("\r", flush=True)
