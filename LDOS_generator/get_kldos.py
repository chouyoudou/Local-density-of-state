import numpy as np
import os

class Get_kldos:
    def __init__(self, eigen, k_index, ldos_dir, charge_density_dir, energy_bin=0.01):
        self.eigen = eigen
        self.k_index = k_index
        self.energy_bin = energy_bin
        self.ldos_dir = ldos_dir
        self.charge_density_dir = charge_density_dir
        os.makedirs(self.ldos_dir, exist_ok=True)

    def run(self):
        energy_min = -30
        energy_max = 30
        data = np.loadtxt(os.path.join(self.charge_density_dir, f'ChargeDensity_k{self.k_index}'), skiprows=1)
        header = np.loadtxt(os.path.join(self.charge_density_dir, f'ChargeDensity_k{self.k_index}'))
        layer_pos = header[0]
        layer = len(layer_pos[1:])
        energy_range = np.arange(energy_min, energy_max, self.energy_bin)
        LDOS = np.zeros((len(energy_range), layer))

        for layer_i in range(layer):
            self.calculate_LDOS(layer_i, energy_range, self.energy_bin, data, LDOS)

        energy_v = energy_range.reshape(len(energy_range), 1)
        output = np.hstack((energy_v, LDOS))
        output = np.vstack((layer_pos, output))
        np.savetxt(os.path.join(self.ldos_dir, f'LDOS_k{self.k_index}'), output)

    def calculate_LDOS(self, layer_i, energy_range, energy_bin, data, LDOS):
        for energy_i in range(len(energy_range)):
            if energy_i == 0:
                continue
            for band_i in range(len(data)):
                if energy_range[energy_i] >= data[band_i][0] > energy_range[energy_i - 1]:
                    LDOS[energy_i][layer_i] = LDOS[energy_i][layer_i] + data[band_i][layer_i + 1]
