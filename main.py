from LDOS_generator.LDOS_generator import LDOS_generator

if __name__ == '__main__':
    k_min = 21
    k_max = 21
    band_min = 1
    band_max = 10
    cube_dir = '~/path/to/cube_files'
    eigenval_path = '~/path/to/EIGENVAL'
    skip = 3  # Adjust the step from which you want to start

    ldos_generator = LDOS_generator(k_min, k_max, band_min, band_max, cube_dir, eigenval_path, skip=skip)
    ldos_generator.prepare_data()
