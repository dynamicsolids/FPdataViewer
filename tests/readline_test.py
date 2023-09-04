import time

import mlab_tools.parsing as p

if __name__ == '__main__':
    with open("../examples/ML_AB_Li3N") as file:
        N = 100

        st = time.time()
        for i in range(N):
            mlab = p.load(file)

            file.seek(0)
        et = time.time()
        print((et - st) / N)
