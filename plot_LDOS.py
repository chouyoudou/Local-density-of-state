import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
# generate 2 2d grids for the x & y bounds
LDOS=np.loadtxt("sum_LDOS",dtype=np.float64,skiprows=1) #skip the first line (label of distance)
energy=LDOS[:,0]
DOS=LDOS[1:,1:]
dis=np.loadtxt("sum_LDOS" ,dtype=np.float64,usecols=range(1,-1)) # skip the first column (label of energy)
dis=dis[0,:]
x=dis
y=energy
z=DOS
x, y = np.meshgrid(x, y)
z_min, z_max = -abs(z).max(), abs(z).max()
ax = plt.subplot(111)

font = {'family' : 'arial',  
        'color'  : 'black',  
        'weight' : 'normal',  
        'size'   : 21,  
        }  

c = ax.pcolormesh(x-20, y, z, cmap='GnBu', norm=LogNorm(vmin=1e-10, vmax=1e-7))

ax.set_title('Local density of states of C-H bond interface',fontdict=font)
ax.set_xlabel(r'Distance ($\AA$)',fontdict=font)
ax.set_ylabel(r'Energy (eV)',fontdict=font)


plt.xticks(fontsize=21,fontname='arial')
plt.yticks(fontsize=21,fontname='arial')

plt.ylim((6, 15)) # set y limits manually
cb = plt.colorbar(c, ax=ax)
cb.set_label('DOS (states/eV)',fontdict=font)
cb.ax.tick_params(labelsize=16)
fig = plt.gcf()


fig.set_size_inches(14,6)
#plt.show()
plt.savefig('LDOS.png',bbox_inches='tight',dpi= 1000,pad_inches=0.0)
