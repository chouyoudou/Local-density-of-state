# Local-density-of-state
This is a tool for calculating the local density of states, which is useful for studying the properties of inhomogeneous system.
## Rendering
![renderings](https://user-images.githubusercontent.com/60209970/224648756-dfc02b7d-462a-4e37-8ad1-861f87c7f218.png)

## Principle
Divide the unit cell into (%custom) thick slices parallel to the interface, and specify each slice as a local ( $\mu \mathrm{th})$ region $\Omega_\mu$, and then define a local density of states $D_\mu(\epsilon)$ of the $\mu$ th region as

$$
\begin{gathered}
D_\mu(\boldsymbol{\epsilon})=\frac{1}{V_{B Z}} \sum_\nu \int \omega_{\boldsymbol{k} \nu}^\mu \delta\left(\boldsymbol{\epsilon}-\boldsymbol{\epsilon}{\boldsymbol{k} \nu}\right) d \boldsymbol{k}, \\
\omega{\boldsymbol{k} \nu}^\mu=\int_{\Omega_\mu} \rho_{\boldsymbol{k} \nu}(\boldsymbol{r}) d \boldsymbol{r},
\end{gathered}
$$


where $\boldsymbol{k}$ denotes a point in the Brillouin zone, $\nu$ is a band index, $V_{B Z}$ is the volume of the Brillouin zone, and $\rho_{k \nu}(r)$ is a partial electron density contributed from an eigenwave function labeled by $\boldsymbol{k}$ and $\nu$. 

## Parameters 
| Name      | Value     | Default | Description                                                                                               |
| --------- | --------- | ------- | --------------------------------------------------------------------------------------------------------- |
| num_threads    | int     |        | This script uses multi-threading to improve speed, so you need to specify the number of threads of the machine. |
| k_min    | int     |        | Specify a k-point range to extract the plane wave coefficients of the Kohn-Sham (KS) orbit from the WAVECAR file and output the real space wave function, corresponding to k_max.|
| k_max | int     |         | Same as k_min |
| band_min | int     |         | Specify the the minimum value of the range of band numbers, same as k_min. |
| band_max | int     |         | Same as band_min. |
| cubetool_path | str     |         | the path of cubetool, which is use to normalize the real and imaginary parts of the .cube file. |
| gcube2oned | str     |         | the path of gcube2oned of OpenMX, which is used to calculate the distribution of charge density in one dimension using .cube files |
