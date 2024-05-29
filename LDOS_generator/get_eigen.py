import numpy as np

def get_eigen(path='', soc=0):
    with open(path+'EIGENVAL', 'r') as f:
        lines = f.readlines()

    enum = int(lines[5].strip().split()[0])
    nkpt = int(lines[5].strip().split()[1])
    nbnd = int(lines[5].strip().split()[2])

    if soc == 0 or soc == 1:
        band = []
        for i in range(nkpt):
            k_idx = 7 + i*(nbnd+2)
            for j in range(nbnd):
                b_idx = k_idx + j + 1
                band.append(float(lines[b_idx].strip().split()[1]))

        bands = np.array(band).reshape(nkpt, nbnd)
        return bands

    elif soc == -1:
        upband = []
        downband = []
        for i in range(nkpt):
            k_idx = 7 + i*(nbnd+2)
            for j in range(nbnd):
                b_idx = k_idx + j + 1
                upband.append(float(lines[b_idx].strip().split()[1]))
                downband.append(float(lines[b_idx].strip().split()[2]))

        upbands = np.array(upband).reshape(nkpt, nbnd)
        downbands = np.array(downband).reshape(nkpt, nbnd)
        return upbands, downbands

