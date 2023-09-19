import time

from mlab.parsing import load
from mlab.validation import validate

with open("/mnt/c/Users/thijm/Documents/PycharmProjects/mlab/examples/ML_AB_BiO_small") as file:
    start = time.perf_counter()
    mlab = load(file)
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    validate(mlab)
    end = time.perf_counter()
    print(end - start)
