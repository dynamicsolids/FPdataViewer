import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
group_foo = parser.add_argument_group("foo")
group_bar = parser.add_argument_group("bar")
group_foo.add_argument("--foobaz", dest="foo.foobaz")
group_bar.add_argument("--barbaz", dest="bar.foobaz")

subparsers = parser.add_subparsers()

subparsers.add_parser("a")
subparsers.add_parser("b")

args = parser.parse_args()
print(vars(args))


def create_tree() -> defaultdict:
    def branch_factory():
        return defaultdict(branch_factory)

    return branch_factory()


res = create_tree()
for key, value in vars(args).items():
    if "." in key:
        key, subkey = key.split(".")
        res[key][subkey] = value
    else:
        res[key] = value

print(res)
