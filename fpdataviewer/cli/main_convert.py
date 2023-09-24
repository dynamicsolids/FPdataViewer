import ase.io

from fpdataviewer.mlab import ase_adapter, parsing


def convert(args) -> None:
    if args.from_format == "vasp-mlab":
        with args.input_file.open(mode="rt") as file:
            mlab = parsing.load(file)
            atoms = ase_adapter.from_mlab(mlab)

        if args.index is not None:
            atoms = atoms[ase.io.string2index(args.index)]
    else:
        atoms = ase.io.read(args.input_file, index=args.index, format=args.from_format)

    ase.io.write(args.output_file, atoms, format=args.to_format, append=args.append)
