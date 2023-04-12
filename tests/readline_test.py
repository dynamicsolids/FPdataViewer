from mlab.parsing import MLABParser
from mlab.parsing_old import MLABParser as MLABParser_old


def old(file):
    parser = MLABParser_old(file)
    mlab = parser.read_mlab()


def new(file):
    parser = MLABParser(file)
    mlab = parser.read_mlab()


if __name__ == '__main__':
    import time

    with open("../example_files/ML_AB_Li3N") as file:
        N = 100

        st = time.time()
        for i in range(N):
            parser = MLABParser(file)
            mlab = parser.read_mlab()

            file.seek(0)
        et = time.time()
        print((et - st) / N)

    # from timeit import timeit, repeat
    #
    # with open("../example_files/ML_AB_Li3N") as file:
    #     glob = {"file": file}
    #
    #     print("Testing old...")
    #     print(repeat("file.seek(0); old(file)", number=100, repeat=3, setup="from __main__ import old", globals=glob))
    #     print("Testing new...")
    #     print(repeat("file.seek(0); new(file)", number=100, repeat=3, setup="from __main__ import new", globals=glob))
