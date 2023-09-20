from fpdataviewer.mlab import parsing, validation


def validate(args):
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)

    print("format ok")

    try:
        validation.validate(mlab)
    except validation.ValidationException as e:
        print(e)
        print("note this may not be the only problem!")
    else:
        print("no problems found")
