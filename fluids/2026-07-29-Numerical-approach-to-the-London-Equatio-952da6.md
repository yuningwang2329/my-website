# Numerical approach to the London Equation of superconductivity

- **作者 (Authors)**: Nicolás Barnafi, Ignacio Labarca-Figueroa, Carlos Román
- **来源 (Source)**: Arxiv (math.AP)
- **日期 (Date)**: 2026-07-29
- **原文链接 (Link)**: [查看原始论文](https://arxiv.org/abs/2607.27103v1)

## 中文摘要

在这项工作中，我们提出了一种通用的离散化策略，用于求解整个空间 $\mathbb{R}^3$ 中的 II 型超导体伦敦方程。为了计算磁场 $H_0$，我们将磁势问题重新表述为传输问题，并通过非标准 FEM-BEM 耦合将其离散化。该公式考虑了有界内部域和无界外部域，而无需引入人工截断。   然后，我们计算矢量场 $B_0$，该矢量场由超导样品中磁势的亥姆霍兹-霍奇分解产生。该场进入等通量问题，该问题确定了超导金兹堡-朗道模型中涡旋成核首先变得能量有利的曲线。我们使用 Kikuchi 的混合公式重新构造 $B_0$ 的方程，其中弱施加无散约束，并使用经典的 $H(\operatorname{curl})$ 符合有限元离散化对结果问题进行离散化。   我们通过收敛测试验证我们的离散化策略，并最终应用到等通量问题。对于处于恒定施加磁场下的球，唯一的最大值是与磁场对齐的直径。对于在与其主轴对齐的恒定外加磁场下的椭球体，我们的计算提供了在足够细长的雪茄形几何形状中不同行为的数值证据：让人想起 U 形涡旋配置的离轴竞争者获得了比主轴更大的等通量比。因此，由于长轴不是最大化器，因此任何离轴最大化器都会通过旋转对称性生成等效配置的连续族，这意味着等通量问题中的非唯一性和简并旋转方向的存在。

---

## 英文摘要

In this work, we propose a general discretization strategy for solving the London equation for type-II superconductors in the whole space $\mathbb{R}^3$. To compute the magnetic field $H_0$, we reformulate the problem for the magnetic potential as a transmission problem and discretize it through a nonstandard FEM-BEM coupling. This formulation accounts for both the bounded interior domain and the unbounded exterior domain without introducing an artificial truncation.   We then compute the vector field $B_0$, which arises from the Helmholtz-Hodge decomposition of the magnetic potential in the superconducting sample. This field enters the isoflux problem, which identifies the curves along which vortex nucleation first becomes energetically favorable in the Ginzburg--Landau model of superconductivity. We recast the equations for $B_0$ using the mixed formulation of Kikuchi, in which the divergence-free constraint is imposed weakly, and discretize the resulting problem using a classical $H(\operatorname{curl})$-conforming finite element discretization.   We validate our discretization strategy through convergence tests and conclude with an application to the isoflux problem. For a ball under a constant applied magnetic field, the unique maximizer is the diameter aligned with the field. For ellipsoids under a constant applied magnetic field aligned with their major axis, our computations provide numerical evidence of a different behavior in sufficiently elongated, cigar-shaped geometries: off-axis competitors reminiscent of U-shaped vortex configurations attain a larger isoflux ratio than the major axis. Since the major axis is therefore not a maximizer, any off-axis maximizer generates, by rotational symmetry, a continuous family of equivalent configurations, implying non-uniqueness and the presence of a degenerate rotational direction in the isoflux problem.
