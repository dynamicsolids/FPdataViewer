from fpdataviewer.mlab import parsing, validation


def inspect(args):
    # Load MLAB file
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)
    if args.strict:
        validation.validate(mlab)
    sections = parsing.split(mlab)

    # Print summary to console
    print(f"file contains {len(sections)} group{'' if len(sections) == 1 else 's'} of structures")
    print()
    for i, section in enumerate(sections):
        atom_repr = ", ".join([f"{name} ({number})" for name, number in section.number_of_atoms_per_type])
        current_group = i + 1
        total_groups = len(sections)

        print(f"[{current_group}/{total_groups}] name       : {section.name}")
        print(f"[{current_group}/{total_groups}] atoms      : {section.number_of_atoms}")
        print(f"[{current_group}/{total_groups}] atom types : {atom_repr}")
        print(f"[{current_group}/{total_groups}] structures : {len(section.configurations)} / {len(section.source.configurations)}")
        print()
