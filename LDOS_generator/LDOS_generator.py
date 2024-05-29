import numpy as np
import os
from .get_eigen import get_eigen
from .gcube2oned import Cube2oned
from .ChargeDensity import ChargeDensity
from .get_kldos import Get_kldos

class LDOS_generator:
    def __init__(self, k_min, k_max, band_min, band_max, cube_dir, eigenval_path, interval=20, skip=0):
        self.k_min = k_min
        self.k_max = k_max
        self.band_min = band_min
        self.band_max = band_max
        self.interval = interval
        self.cube_dir = cube_dir
        self.eigenval_path = eigenval_path
        self.skip = skip

        self.eigen = get_eigen(eigenval_path)
        self.ldos_dir = os.path.join(cube_dir, 'LDOS')
        self.charge_density_dir = os.path.join(cube_dir, 'ChargeDensity')
        self.oned_dir = os.path.join(cube_dir, '1d')

    def prepare_data(self):

        for k_i in range(self.k_min, self.k_max + 1):
            if self.skip <= 1:
                print('------------------  K %i Step 1, get .1d file ------------------' % k_i)
                for band_i in range(self.band_min, self.band_max + 1):
                    input_file = os.path.join(self.cube_dir, f'B{band_i}_K{k_i}.cube')
                    axis = 3  # Assuming we are using axis 3 as in the original C code
                    processor = Cube2oned(input_file, axis, self.oned_dir)
                    processor.save_1d_file()

            if self.skip <= 2:
                print('------------------  K %i Step 2, get charge density ------------------' % k_i)
                chargedensity = ChargeDensity(self.eigen, self.band_min, self.band_max, k_i, self.interval, self.charge_density_dir, self.oned_dir)
                chargedensity.run()

            if self.skip <= 3:
                print('------------------  K %i Step 3, get LDOS ------------------' % k_i)
                kldos = Get_kldos(self.eigen, k_i, self.ldos_dir, self.charge_density_dir)
                kldos.run()

        if self.skip <= 4:
            print('------------------   Final step, get sum_LDOS ------------------')
            self.sum_LDOS()

    def sum_LDOS(self):
        header = np.loadtxt(os.path.join(self.ldos_dir, f"LDOS_k{self.k_min}"), dtype=np.float64)
        data_sum = np.loadtxt(os.path.join(self.ldos_dir, f"LDOS_k{self.k_min}"), dtype=np.float64, skiprows=1)
        for k_index in range(self.k_min + 1, self.k_max + 1):
            data_tmp = np.loadtxt(os.path.join(self.ldos_dir, f"LDOS_k{k_index}"), dtype=np.float64, skiprows=1)
            data_sum = data_sum + data_tmp
            print(f'sum k{k_index}')

        data_sum = np.vstack((header[0], data_sum))
        data_sum[:, 0] = header[:, 0]
        np.savetxt(os.path.join(self.ldos_dir, 'sum_LDOS'), data_sum)
