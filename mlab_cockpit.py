import argparse

from mlab.initialization import init, print_stats
from mlab_hist import view as hist_view

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="reads ML_AB files and displays various statistics")

    groups, config = init(parser)

    for group in groups:
        print_stats(group, config)
        hist_view(group, config)
