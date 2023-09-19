import json

from mlab import parsing, validation
from src.internal.config import set_config, default_config


def exec(args):
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
    sections = parsing.split(mlab)

    # Plot
    if args.interactive:
        import src.internal.output.output_plt as output
    else:
        import src.internal.output.output_pdf as output

    output.run(args, mlab, sections)

    print("\r")
