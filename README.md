# Local-density-of-state
This is a tool for calculating the local density of states, which is useful for studying the properties of inhomogeneous media.
## Rendering
![renderings](https://user-images.githubusercontent.com/60209970/224648756-dfc02b7d-462a-4e37-8ad1-861f87c7f218.png)

## Priciple
Divide the unit cell into ($custom) thick slices parallel to the interface, and specify each slice as a local ( $\mu \mathrm{th})$ region $\Omega_\mu$, and then define a local density of states $D_\mu(\epsilon)$ of the $\mu$ th region as

$$
\begin{gathered}
D_\mu(\boldsymbol{\epsilon})=\frac{1}{V_{B Z}} \sum_\nu \int \omega_{\boldsymbol{k} \nu}^\mu \delta\left(\boldsymbol{\epsilon}-\boldsymbol{\epsilon}_{\boldsymbol{k} \nu}\right) d \boldsymbol{k}, \\
\omega_{\boldsymbol{k} \nu}^\mu=\int_{\Omega_\mu} \rho_{\boldsymbol{k} \nu}(\boldsymbol{r}) d \boldsymbol{r},
\end{gathered}
$$
