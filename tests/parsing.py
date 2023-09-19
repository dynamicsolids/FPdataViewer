import time
from typing import TextIO

import mlab.parsing_new

import mlab.parsing


def old(file: TextIO):
    file.seek(0)
    _ = mlab.parsing.load(file)

def new(file: TextIO):
    file.seek(0)
    _ = mlab.parsing_new.load(file)

with open("/mnt/c/Users/thijm/Documents/PycharmProjects/mlab/examples/ML_AB_BN") as file:
    print("warming up")
    for _ in range(10):
        old(file)
        new(file)

    N = 20
    M = 2

    for _ in range(M):
        print("old: ", end="")
        start = time.perf_counter()
        for _ in range(N):
            old(file)
        end = time.perf_counter()
        print(f"{(end - start) * 1000. / N:.0f} ms")

        print("new: ", end="")
        start = time.perf_counter()
        for _ in range(N):
            new(file)
        end = time.perf_counter()
        print(f"{(end - start) * 1000. / N:.0f} ms")

# with open("/mnt/c/Users/thijm/Documents/PycharmProjects/mlab/examples/ML_ABCAR-MAPbI1.5Br1.5") as file:
#     for _ in range(10):
#         new(file)
