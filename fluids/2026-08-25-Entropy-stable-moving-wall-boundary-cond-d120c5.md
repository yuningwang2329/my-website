# Entropy-stable moving-wall boundary conditions for the ALE formulation of the compressible Navier-Stokes equations

- **作者 (Authors)**: Luca Galimberti, Roberto Nuca, Lisandro Dalcin, Alberto Guardone, Matteo Parsani
- **来源 (Source)**: Arxiv (math.AP)
- **日期 (Date)**: 2026-08-25
- **原文链接 (Link)**: [查看原始论文](https://arxiv.org/abs/2608.25146v1)

## 中文摘要

我们提出了运动域上可压缩欧拉和纳维-斯托克斯方程的高阶熵稳定框架。描述域运动的时空映射以任意拉格朗日欧拉 (ALE) 公式进行重新设计，其中物理无粘通量和网格运动引起的贡献以统一的方式处理。在连续水平上，我们证明所提出的移动壁边界条件对于欧拉方程是熵保守的，对于纳维-斯托克斯方程是熵稳定的。无滑移条件是根据相对于移动壁的速度来表述的，产生对熵平衡的有界无粘性贡献，而粘性项仅贡献熵耗散。使用对角范数分部求和 (SBP) 算子以及适当的数值通量，这些属性可以扩展到半离散公式，从而产生 $L^2$ 意义上的非线性稳定性。该方法的准确性、鲁棒性和可扩展性在实践中通过大量的数值实验得到了证明，从典型的二维验证​​案例到涉及移动边界和流固相互作用的大规模湍流和超音速模拟。结果证实了高阶熵稳定方案适用于各种流态和多物理场应用中的复杂运动域问题。由于分析依赖于 SBP 属性而不是特定的离散化，因此该框架自然地扩展到基于对角范数 SBP 算子的广泛方法，包括有限体积、有限元和通量重建方案。

---

## 英文摘要

We present a high-order entropy-stable framework for the compressible Euler and Navier-Stokes equations on moving domains. The space-time mapping describing the domain motion is recast in an arbitrary Lagrangian Eulerian (ALE) formulation, in which the physical inviscid fluxes and the contributions induced by mesh motion are treated in a unified manner. At the continuous level, we prove that the proposed moving-wall boundary conditions are entropy conservative for the Euler equations and entropy stable for the Navier-Stokes equations. The no-slip condition is formulated in terms of the velocity relative to the moving wall, yielding a bounded inviscid contribution to the entropy balance, while the viscous terms contribute only entropy dissipation. Using diagonal norm summation-by-parts (SBP) operators together with appropriate numerical fluxes, these properties are extended to the semi-discrete formulation, resulting in nonlinear stability in the $L^2$ sense. The accuracy, robustness, and scalability of the proposed method are demonstrated in practice through an extensive set of numerical experiments, ranging from canonical two-dimensional verification cases to large-scale turbulent and supersonic simulations involving moving boundaries and fluid-structure interaction. The results confirm the suitability of high-order entropy-stable schemes for complex moving-domain problems across a broad range of flow regimes and multiphysics applications. Because the analysis relies on the SBP property rather than on a particular discretization, the framework naturally extends to a broad class of methods based on diagonal-norm SBP operators, including finite volume, finite element, and flux reconstruction schemes.
