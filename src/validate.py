from mlab import parsing, validation
from mlab.validation import ValidationException


def exec(args):
    with args.input_file.open(mode="rt") as file:
        mlab = parsing.load(file)

    try:
        validation.validate(mlab)
    except ValidationException as e:
        print(f"a problem was found: {e}")
        print("note this may not be the only problem!")
    else:
        print("no problems found")
