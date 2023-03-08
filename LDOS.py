import numpy as np
import os
import threading
import queue
import concurrent.futures

def vaspkit4cube(q):
    while True:
        item = q.get()
        if item is None:
            break
        k_i, band_i = item
        os.system('vaspkit -task 512 -ikpt %i -iband %i >> vaspkit.log' %(k_i, band_i))
        q.task_done()

def get_cube(band_min, band_max, k_i, num_threads):
    q = queue.Queue()
    for band_i in range(band_min, band_max+1):
        q.put((k_i, band_i))
    for _ in range(num_threads):
        t = threading.Thread(target=vaspkit4cube, args=(q,))
        t.start()
    q.join()
    for _ in range(num_threads):
        q.put(None)

def norm_cube(band_min, band_max, k_i, cubetool_path,num_threads):
    q = queue.Queue()
    threads = []
    for band_i in range(band_min, band_max+1):
        command = '%s WFN_IMAG_B%s_K%s.vasp.cube WFN_REAL_B%s_K%s_UP.vasp.cube norm > B%i_K%i.cube &' %(cubetool_path, str(band_i).zfill(4), str(k_i).zfill(4), str(band_i).zfill(4), str(k_i).zfill(4), band_i, k_i)
        q.put(command)

    def worker():
        while True:
            item = q.get()
            if item is None:
                break
            os.system(item)
            q.task_done()

    for i in range(num_threads):  
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    q.join()

def get_1d(gcube2oned_path, band_min, band_max, k_i, num_threads):
    threads = []
    for band_i in range(band_min, band_max + 1):
        t = threading.Thread(target=run_1d, args=(gcube2oned_path, band_i, k_i))
        threads.append(t)
    # start threads
    for i in range(0, len(threads), num_threads):
        for j in range(i, min(i + num_threads, len(threads))):
            threads[j].start()
        for j in range(i, min(i + num_threads, len(threads))):
            threads[j].join()

def run_1d(gcube2oned_path, band_i, k_i):
    os.system('%s B%i_K%i.cube 3 > B%i_K%i.1d' % (gcube2oned_path, band_i, k_i, band_i, k_i))



def calculate_LDOS_thread(layer_i, energy_range, energy_bin, data, LDOS):
    for energy_i in range(len(energy_range)):
        if energy_i == 0:
            continue
        for band_i in range(len(data)):
            if energy_range[energy_i] >= data[band_i][0] > energy_range[energy_i - 1]:
                LDOS[energy_i][layer_i] = LDOS[energy_i][layer_i] + data[band_i][layer_i + 1]

def cal_LDOS(eigen, k_index, num_threads, energy_bin=0.01):
    # Energy range defined as the min and max of the Eigen Value of the band
    energy_min = -30
    energy_max = 30

    # Load and define
    data = np.loadtxt('integral_k%i' % k_index, skiprows=1)
    header = np.loadtxt('integral_k%i' % k_index)
    layer_pos = header[0]
    layer = len(layer_pos[1:])  # number of layer, data[0][0] has no meaning, skip it.
    energy_range = np.arange(energy_min, energy_max, energy_bin)
    LDOS = np.zeros((len(energy_range), layer))
    threads = []

    # Create threads
    for layer_i in range(layer):
        t = threading.Thread(target=calculate_LDOS_thread,
                             args=(layer_i, energy_range, energy_bin, data, LDOS))
        threads.append(t)

    # Start threads
    for t in threads:
        t.start()

    # Wait for threads to finish
    for t in threads:
        t.join()

    # Save output to file
    energy_v = energy_range.reshape(len(energy_range), 1)
    output = np.hstack((energy_v, LDOS))
    output = np.vstack((layer_pos, output))
    np.savetxt('LDOS_k%i' % k_index, output)
    


def trap_comp(data, start, end, h):
    return np.sum(h * (data[start:end, 2] + data[start+1:end+1, 2]) / 2)


def compute_integral(q, eigen, band_min, band_max, k_i, interval, num_threads):
    data = np.loadtxt("B%d_K%d.1d" % (band_min, k_i), dtype=np.float64)
    dis = data[1, 1]  # distance of each layer

    list_dis = np.arange(interval, len(data), interval) * dis
    integral_D_I = np.concatenate(([0], list_dis))

    h = np.full_like(data[:, 1], dis)
    np.put(h, [0, -1], dis/2)

    for band in range(band_min, band_max+1):
        list_1band = np.zeros(len(list_dis) + 1)
        list_1band[0] = eigen[k_i-1, band-1]
        steps = np.arange(interval, len(data), interval)

        lock = threading.Lock()
        def worker(start, end):
            integral = trap_comp(data, start, end, h)
            with lock:
                list_1band[(start+interval)//interval] = integral

        threads = []
        for i in range(num_threads):
            start = i * len(steps) // num_threads
            end = (i+1) * len(steps) // num_threads
            t = threading.Thread(target=worker, args=(steps[start]-interval, steps[end-1],))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        integral_D_I = np.vstack((integral_D_I, list_1band))

    q.put((k_i, integral_D_I))


def integral(eigen, band_min, band_max, num_kpoints, num_threads=4, interval=20):
    ''' interval = How many layer in .1d for one layer in integral'''

    q = queue.Queue()
    threads = []

    for k_i in range(1, num_kpoints+1):
        t = threading.Thread(target=compute_integral, args=(q, eigen, band_min, band_max, k_i, interval, num_threads))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    result = {}
    while not q.empty():
        k_i, integral_D_I = q.get()
        result[k_i] = integral_D_I

    for k_i, integral_D_I in result.items():
        np.savetxt('integral_k%i' % k_i, integral_D_I)


def GetEiGen(path='',soc=0):                                   # extract band information from EIGENVAL
    #Returns a matrix, the first element is the k-point index, and the second element is the Eigen Value corresponding to the energy band
	with open(path+'EIGENVAL','r') as f:
		lines = f.readlines()

	enum = int(lines[5].strip().split()[0])       # number of electrons
	nkpt = int(lines[5].strip().split()[1])       # number of KPOINTS
	nbnd = int(lines[5].strip().split()[2])       # number of bands
	
	if soc == 0 or soc == 1:        
		band = []; kpt = []
		for i in range(nkpt):
			k_idx = 7 + i*(nbnd+2)
			for j in range(nbnd):
				b_idx = k_idx + j + 1
				band.append(float(lines[b_idx].strip().split()[1]))

		bands = np.array(band).reshape(nkpt,nbnd)
		return bands

	elif soc == -1:
		upband = []; downband = [];kpt = []
		for i in range(nkpt):
			k_idx = 7 + i*(nbnd+2)
			for j in range(nbnd):
				b_idx = k_idx + j + 1
				upband.append(float(lines[b_idx].strip().split()[1]))
				downband.append(float(lines[b_idx].strip().split()[2]))

		upbands = np.array(upband).reshape(nkpt,nbnd)
		downbands = np.array(downband).reshape(nkpt,nbnd)
		return upbands,downbands


def sum_LDOS(k_min, k_max):
    header=np.loadtxt("LDOS_k%i" %k_min,dtype=np.float64)  #Read the distance of the first line, and add the LDOS file at the end, otherwise there will be an error when summing
    data_sum=np.loadtxt("LDOS_k%i" %k_min,dtype=np.float64,skiprows=1)   # skiprows=1 is the distance to skip the first row
    for k_index in range(k_min+1, k_max):
        data_tmp=np.loadtxt("LDOS_k%i" %k_index,dtype=np.float64,skiprows=1)
        data_sum=data_sum+data_tmp
        print('sum k%i' %k_index)


    data_sum = np.vstack((header[0], data_sum))
    data_sum[:,0]=header[:,0]   # Return the energy of the first column to normal
    #print(data_sum[1,:])
    np.savetxt('sum_LDOS',data_sum) 
    #print(header[0],data_sum[1,:])

def prepare_data(k_min, k_max, band_min, band_max, cubetool_path, gcube2oned_path, num_threads, rm_data=True):
    eigen = GetEiGen()
    os.system('ulimit -s unlimited')
    
    for k_i in range(k_min, k_max+1):

        if rm_data :
            os.system('rm *.cube')
 
        print('------------------  K %i Step 1, get cube ------------------' %k_i)
        get_cube(band_min, band_max, k_i, num_threads)
  
        print('------------------  K %i Step 2, norm cube ------------------' %k_i)
        norm_cube(band_min, band_max, k_i, cubetool_path,num_threads)
        
        print('------------------  K %i Step 3, get .1d file ------------------' %k_i)
        get_1d(gcube2oned_path, band_min, band_max, k_i, num_threads)
        
        print('------------------  K %i Step 4, get charge density ------------------' %k_i)
        integral(eigen, band_min, band_max, k_i, num_threads, interval=20)
        
        print('------------------  K %i Step 5, get LDOS ------------------' %k_i)
        cal_LDOS(eigen, k_i, num_threads, energy_bin=0.01)
        
    print('------------------   Finall step, get sum_LDOS ------------------')
    sum_LDOS(k_min, k_max+1)



### Parameter ###
k_min=21
k_max=21
band_min=1
band_max=10
cubetool_path='~/package/cubeTool/cubeTool'
gcube2oned_path='~/openmx3.9/source/gcube2oned'

num_threads=128
prepare_data(k_min, k_max, band_min, band_max, cubetool_path, gcube2oned_path, num_threads)



