# Analysis of Moment Closures Using $\varphi$-Divergences for Rarefied Dynamics with Binary Collisions and Their Galerkin Discretizations

- **作者 (Authors)**: Michael R. A. Abdelmalik, Irene M. Gamba, Torsten Kessler, Sergej Rjasanow
- **来源 (Source)**: Arxiv (math.AP)
- **日期 (Date)**: 2026-08-04
- **原文链接 (Link)**: [查看原始论文](https://arxiv.org/abs/2608.03640v1)

## 中文摘要

这项工作引入了一个鲁棒的确定性框架，通过使用伽辽金方法离散化玻尔兹曼方程对时间、位置和速度的依赖性，来近似二元碰撞的玻尔兹曼方程的解。通过采用基于速度空间 $\varphi$-散度的一系列参数伽辽金闭包，我们推导出控制流体动力学变量的严格的力矩方程层次结构。为了解决这些闭包本身不能保证真正二元碰撞算子的散度熵消散的限制，我们通过制定适合每个闭包的兼容近似碰撞算子来恢复此属性。这个构造的算子本质上保留了高保真流动模拟所必需的基本物理特性，包括伽利略不变性、质量、动量和能量的精确守恒，以及$\varphi$散度熵的严格耗散。此外，我们表明所得到的闭矩系统是对称耗散的，产生局部时间适定的柯西问题。为了将这一数学基础转化为有效的计算工具，我们使用熵稳定的不连续伽辽金 (DG) 有限元方法离散化位置和时间变量。完全隐式、熵稳定的时空方法使时间步长远远超出典型的 CFL 限制步长和稳态的直接计算。通过对超音速喷嘴氩气流量、通道质量流量以及平行壁之间的传热进行数值模拟，验证了该方法的鲁棒性和准确性，证明了与分析基准、实验测量和随机粒子模拟的一致性。

---

## 英文摘要

This work introduces a robust deterministic framework for approximating solutions of the Boltzmann equation with binary collisions by discretizing their dependence on time, position, and velocity using Galerkin methods. By employing a family of parametric Galerkin closures based on $\varphi$-divergences in velocity space, we derive rigorous hierarchies of moment equations that govern fluid dynamic variables. Addressing the limitation that these closures alone do not guarantee dissipation of a $\varphi$-divergence entropy for the true binary collision operator, we restore this property by formulating a compatible approximate collision operator tailored to each closure. This constructed operator intrinsically retains fundamental physical properties essential for high-fidelity flow simulations, including Galilean invariance, exact conservation of mass, momentum, and energy, and strict dissipation of a $\varphi$-divergence entropy. Furthermore, we show that the resulting closed moment systems are symmetric-dissipative, yielding Cauchy problems that are well-posed locally in time. To translate this mathematical foundation into an efficient computational tool, we discretize the position and time variables with an entropy-stable discontinuous Galerkin (DG) finite element method. The fully implicit, entropy-stable space-time approach enables time steps far beyond typical CFL-limited step sizes and the direct computation of steady states. The robustness and accuracy of the methodology are verified and validated through numerical simulations on the supersonic nozzle flow of argon, mass flow through a channel, and heat transfer between parallel walls, demonstrating agreement with analytical benchmarks, experimental measurements, and stochastic particle simulations.
