import numpy as np
import os

class ChargeDensity:
    def __init__(self, eigen, band_min, band_max, k_i, interval, output_dir, oned_dir):
        self.eigen = eigen
        self.band_min = band_min
        self.band_max = band_max
        self.k_i = k_i
        self.interval = interval
        self.output_dir = output_dir
        self.oned_dir = oned_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        data = np.loadtxt(os.path.join(self.oned_dir, f"B{self.band_min}_K{self.k_i}.1d"), dtype=np.float64)
        dis = data[1, 1]
        list_dis = np.arange(self.interval, len(data), self.interval) * dis
        integral_D_I = np.concatenate(([0], list_dis))
        h = np.full_like(data[:, 1], dis)
        np.put(h, [0, -1], dis / 2)

        for band in range(self.band_min, self.band_max + 1):
            list_1band = np.zeros(len(list_dis) + 1)
            list_1band[0] = self.eigen[self.k_i - 1, band - 1]
            steps = np.arange(self.interval, len(data), self.interval)

            for i in range(len(steps) - 1):
                integral = self.trap_comp(data, steps[i] - self.interval, steps[i], h)
                list_1band[(steps[i] + self.interval) // self.interval] = integral

            integral_D_I = np.vstack((integral_D_I, list_1band))

        np.savetxt(os.path.join(self.output_dir, f'ChargeDensity_k{self.k_i}'), integral_D_I)

    def trap_comp(self, data, start, end, h):
        return np.sum(h * (data[start:end, 2] + data[start + 1:end + 1, 2]) / 2)
