import numpy as np
import os

class Cube2oned:
    def __init__(self, cube_file, axis, output_dir):
        self.cube_file = cube_file
        self.axis = axis - 1  # Convert to 0-based index
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.atom_num, self.grid_origin, self.grid_dims, self.grid_vectors, self.atoms, self.cube_data = self.read_cube_file()

    def read_cube_file(self):
        with open(self.cube_file, 'r') as f:
            # Read and ignore the first two lines (title and comments)
            title = f.readline()
            comment = f.readline()

            # Read the atom number and grid origin
            atom_num = int(f.readline().split()[0])
            grid_origin = np.array(list(map(float, f.readline().split())))

            # Read the grid dimensions and grid vectors
            grid_dims = []
            grid_vectors = []
            for _ in range(3):
                grid_info = f.readline().split()
                grid_dims.append(int(grid_info[0]))
                grid_vectors.append(list(map(float, grid_info[1:])))

            # Read the atom coordinates
            atoms = []
            for _ in range(atom_num):
                atom_info = f.readline().split()
                atoms.append(list(map(float, atom_info[2:])))

            # Read the cube data
            cube_data = np.zeros(grid_dims)
            line_index = 0
            while line_index < np.prod(grid_dims):
                line_data = f.readline().split()
                for value in line_data:
                    i = (line_index // (grid_dims[1] * grid_dims[2])) % grid_dims[0]
                    j = (line_index // grid_dims[2]) % grid_dims[1]
                    k = line_index % grid_dims[2]
                    cube_data[i, j, k] = float(value)
                    line_index += 1

        return atom_num, grid_origin, grid_dims, grid_vectors, atoms, cube_data

    def integrate_3d_to_1d(self):
        step = np.linalg.norm(self.grid_vectors[self.axis])
        integrated_data = []

        if self.axis == 0:
            for i in range(self.cube_data.shape[0]):
                sum_val = np.sum(self.cube_data[i, :, :])
                integrated_data.append((i, step * i, sum_val / (self.cube_data.shape[1] * self.cube_data.shape[2])))
        elif self.axis == 1:
            for j in range(self.cube_data.shape[1]):
                sum_val = np.sum(self.cube_data[:, j, :])
                integrated_data.append((j, step * j, sum_val / (self.cube_data.shape[0] * self.cube_data.shape[2])))
        elif self.axis == 2:
            for k in range(self.cube_data.shape[2]):
                sum_val = np.sum(self.cube_data[:, :, k])
                integrated_data.append((k, step * k, sum_val / (self.cube_data.shape[0] * self.cube_data.shape[1])))

        return integrated_data

    def save_1d_file(self):
        integrated_data = self.integrate_3d_to_1d()
        output_file = os.path.join(self.output_dir, os.path.splitext(os.path.basename(self.cube_file))[0] + '.1d')
        with open(output_file, 'w') as f:
            for data in integrated_data:
                f.write(f"{data[0]:5d} {data[1]:18.15f} {data[2]:18.15f}\n")
